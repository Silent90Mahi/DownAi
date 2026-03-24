"""
Recommendation Service Module

Implements multiple recommendation algorithms for the SHG e-commerce platform:
- Collaborative Filtering (User-based with cosine similarity)
- Content-Based Filtering (Product attributes similarity)
- Knowledge Graph (Relationship traversal)
- Trust-Weighted Ranking (Seller trust score weighting)
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import math
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models


@dataclass
class GraphEdge:
    source: str
    source_id: int
    target: str
    target_id: int
    weight: float = 1.0
    relation_type: str = ""


@dataclass
class KnowledgeGraph:
    shg_to_products: Dict[int, Set[int]] = field(default_factory=lambda: defaultdict(set))
    product_to_category: Dict[int, str] = field(default_factory=dict)
    product_to_subcategory: Dict[int, Optional[str]] = field(default_factory=dict)
    product_to_tags: Dict[int, List[str]] = field(default_factory=lambda: defaultdict(list))
    user_to_preferences: Dict[int, Dict[str, float]] = field(default_factory=lambda: defaultdict(dict))
    user_to_products: Dict[int, Set[int]] = field(default_factory=lambda: defaultdict(set))
    category_to_products: Dict[str, Set[int]] = field(default_factory=lambda: defaultdict(set))
    edges: List[GraphEdge] = field(default_factory=list)
    
    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)
        
        if edge.source == "shg" and edge.target == "product":
            self.shg_to_products[edge.source_id].add(edge.target_id)
        elif edge.source == "product" and edge.target == "category":
            self.product_to_category[edge.source_id] = edge.relation_type
            self.category_to_products[edge.relation_type].add(edge.source_id)
        elif edge.source == "user" and edge.target == "preference":
            self.user_to_preferences[edge.source_id][edge.relation_type] = edge.weight
        elif edge.source == "user" and edge.target == "product":
            self.user_to_products[edge.source_id].add(edge.target_id)


@dataclass
class ProductRecommendation:
    product_id: int
    product: models.Product
    score: float
    recommendation_type: str
    trust_weighted_score: float = 0.0
    seller_trust_score: float = 0.0


@dataclass
class SHGRecommendation:
    shg_id: int
    shg: models.User
    score: float
    recommendation_reason: str
    trust_score: float = 0.0


class RecommendationService:
    """
    Main recommendation service implementing multiple algorithms.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._graph: Optional[KnowledgeGraph] = None
        self._user_vectors: Dict[int, Dict[int, float]] = {}
        self._product_cache: Dict[int, models.Product] = {}
    
    async def _build_knowledge_graph(self) -> KnowledgeGraph:
        """
        Build the knowledge graph from database entities.
        Creates edges for: SHG -> Product, Product -> Category, User -> Preference
        """
        graph = KnowledgeGraph()
        
        products_result = await self.db.execute(
            select(models.Product).where(models.Product.status == models.ProductStatus.ACTIVE)
        )
        products = products_result.scalars().all()
        
        for product in products:
            self._product_cache[product.id] = product
            
            graph.add_edge(GraphEdge(
                source="shg",
                source_id=product.seller_id,
                target="product",
                target_id=product.id,
                weight=product.quality_rating / 5.0 if product.quality_rating > 0 else 0.5
            ))
            
            graph.add_edge(GraphEdge(
                source="product",
                source_id=product.id,
                target="category",
                target_id=0,
                relation_type=product.category
            ))
            
            if product.subcategory:
                graph.product_to_subcategory[product.id] = product.subcategory
            
            if product.tags:
                graph.product_to_tags[product.id] = product.tags if isinstance(product.tags, list) else []
        
        orders_result = await self.db.execute(
            select(models.Order).where(
                models.Order.order_status.in_([
                    models.OrderStatus.DELIVERED,
                    models.OrderStatus.CONFIRMED,
                    models.OrderStatus.SHIPPED
                ])
            )
        )
        orders = orders_result.scalars().all()
        
        order_ids = [order.id for order in orders]
        
        if order_ids:
            items_result = await self.db.execute(
                select(models.OrderItem).where(models.OrderItem.order_id.in_(order_ids))
            )
            order_items = items_result.scalars().all()
            
            order_to_buyer = {order.id: order.buyer_id for order in orders}
            
            for item in order_items:
                buyer_id = order_to_buyer.get(item.order_id)
                if buyer_id:
                    graph.add_edge(GraphEdge(
                        source="user",
                        source_id=buyer_id,
                        target="product",
                        target_id=item.product_id,
                        weight=item.quantity
                    ))
        
        buyers_result = await self.db.execute(
            select(models.Buyer).where(models.Buyer.preferred_categories.isnot(None))
        )
        buyers = buyers_result.scalars().all()
        
        for buyer in buyers:
            if buyer.preferred_categories:
                categories = buyer.preferred_categories if isinstance(buyer.preferred_categories, list) else []
                for category in categories:
                    graph.add_edge(GraphEdge(
                        source="user",
                        source_id=buyer.user_id,
                        target="preference",
                        target_id=0,
                        weight=1.0,
                        relation_type=category
                    ))
        
        self._graph = graph
        return graph
    
    async def _get_or_build_graph(self) -> KnowledgeGraph:
        """Get existing graph or build new one."""
        if self._graph is None:
            return await self._build_knowledge_graph()
        return self._graph
    
    def _cosine_similarity(self, vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
        """
        Calculate cosine similarity between two sparse vectors.
        
        Args:
            vec1: First sparse vector as dict {item_id: value}
            vec2: Second sparse vector as dict {item_id: value}
        
        Returns:
            Cosine similarity score between 0 and 1
        """
        common_keys = set(vec1.keys()) & set(vec2.keys())
        
        if not common_keys:
            return 0.0
        
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _build_user_vectors(self) -> Dict[int, Dict[int, float]]:
        """
        Build user interaction vectors for collaborative filtering.
        Each user is represented as a sparse vector of product interactions.
        """
        if self._user_vectors:
            return self._user_vectors
        
        user_vectors: Dict[int, Dict[int, float]] = defaultdict(dict)
        
        orders_result = await self.db.execute(
            select(models.Order, models.OrderItem)
            .join(models.OrderItem, models.Order.id == models.OrderItem.order_id)
            .where(
                models.Order.order_status.in_([
                    models.OrderStatus.DELIVERED,
                    models.OrderStatus.CONFIRMED
                ])
            )
        )
        
        for order, item in orders_result:
            user_id = order.buyer_id
            product_id = item.product_id
            quantity = item.quantity
            
            if product_id in user_vectors[user_id]:
                user_vectors[user_id][product_id] += quantity
            else:
                user_vectors[user_id][product_id] = float(quantity)
        
        transactions_result = await self.db.execute(
            select(models.Transaction).where(
                models.Transaction.payment_status == "Completed"
            )
        )
        transactions = transactions_result.scalars().all()
        
        for txn in transactions:
            if txn.buyer_id and txn.product_id:
                if txn.product_id in user_vectors[txn.buyer_id]:
                    user_vectors[txn.buyer_id][txn.product_id] += txn.quantity
                else:
                    user_vectors[txn.buyer_id][txn.product_id] = float(txn.quantity)
        
        self._user_vectors = dict(user_vectors)
        return self._user_vectors
    
    async def _find_similar_users(
        self,
        user_id: int,
        min_similarity: float = 0.1,
        max_users: int = 50
    ) -> List[Tuple[int, float]]:
        """
        Find similar users based on order history using cosine similarity.
        
        Args:
            user_id: Target user ID
            min_similarity: Minimum similarity threshold
            max_users: Maximum number of similar users to return
        
        Returns:
            List of (user_id, similarity_score) tuples sorted by similarity
        """
        user_vectors = await self._build_user_vectors()
        
        if user_id not in user_vectors:
            return []
        
        target_vector = user_vectors[user_id]
        similarities: List[Tuple[int, float]] = []
        
        for other_user_id, other_vector in user_vectors.items():
            if other_user_id == user_id:
                continue
            
            similarity = self._cosine_similarity(target_vector, other_vector)
            
            if similarity >= min_similarity:
                similarities.append((other_user_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_users]
    
    async def _calculate_product_similarity(
        self,
        product1: models.Product,
        product2: models.Product
    ) -> float:
        """
        Calculate similarity between two products based on attributes.
        
        Factors:
        - Category match (weight: 0.4)
        - Subcategory match (weight: 0.2)
        - Price similarity (weight: 0.2)
        - Tag overlap (weight: 0.2)
        
        Returns:
            Similarity score between 0 and 1
        """
        score = 0.0
        
        if product1.category == product2.category:
            score += 0.4
        
        if (product1.subcategory and product2.subcategory and 
            product1.subcategory == product2.subcategory):
            score += 0.2
        
        if product1.price > 0 and product2.price > 0:
            max_price = max(product1.price, product2.price)
            min_price = min(product1.price, product2.price)
            price_similarity = min_price / max_price
            score += 0.2 * price_similarity
        
        tags1 = set(product1.tags) if product1.tags else set()
        tags2 = set(product2.tags) if product2.tags else set()
        
        if tags1 and tags2:
            tag_overlap = len(tags1 & tags2) / len(tags1 | tags2)
            score += 0.2 * tag_overlap
        
        return score
    
    async def _apply_trust_weighting(
        self,
        recommendations: List[ProductRecommendation]
    ) -> List[ProductRecommendation]:
        """
        Apply trust-weighted ranking to recommendations.
        
        Formula: final_score = base_score * (1 + (trust_score / 100))
        
        Products from higher trust SHGs get boosted scores.
        """
        for rec in recommendations:
            seller = rec.product.seller
            trust_score = seller.trust_score if seller else 50.0
            
            rec.seller_trust_score = trust_score
            rec.trust_weighted_score = rec.score * (1 + (trust_score / 100))
        
        recommendations.sort(key=lambda x: x.trust_weighted_score, reverse=True)
        return recommendations
    
    async def _get_user_purchased_products(self, user_id: int) -> Set[int]:
        """Get set of products already purchased by user."""
        purchased = set()
        
        orders_result = await self.db.execute(
            select(models.OrderItem.product_id)
            .join(models.Order, models.OrderItem.order_id == models.Order.id)
            .where(models.Order.buyer_id == user_id)
            .distinct()
        )
        
        for row in orders_result:
            purchased.add(row[0])
        
        return purchased
    
    async def _get_user_interacted_shgs(self, user_id: int) -> Set[int]:
        """Get set of SHGs user has interacted with."""
        shgs = set()
        
        orders_result = await self.db.execute(
            select(models.Order.seller_id)
            .where(models.Order.buyer_id == user_id)
            .distinct()
        )
        
        for row in orders_result:
            shgs.add(row[0])
        
        return shgs
    
    async def _collaborative_filtering(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """
        User-based collaborative filtering using cosine similarity.
        Find similar users and recommend products they purchased.
        """
        recommendations: Dict[int, ProductRecommendation] = {}
        
        similar_users = await self._find_similar_users(user_id)
        
        if not similar_users:
            return []
        
        user_vectors = await self._build_user_vectors()
        target_products = user_vectors.get(user_id, {})
        
        for similar_user_id, similarity in similar_users:
            similar_products = user_vectors.get(similar_user_id, {})
            
            for product_id, interaction_weight in similar_products.items():
                if product_id in target_products:
                    continue
                
                if product_id not in self._product_cache:
                    continue
                
                product = self._product_cache[product_id]
                
                score = similarity * interaction_weight
                
                if product_id in recommendations:
                    recommendations[product_id].score += score
                else:
                    recommendations[product_id] = ProductRecommendation(
                        product_id=product_id,
                        product=product,
                        score=score,
                        recommendation_type="collaborative_filtering"
                    )
        
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x.score,
            reverse=True
        )
        
        return sorted_recs[:limit * 2]
    
    async def _content_based_filtering(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """
        Content-based filtering using product attributes.
        Recommend products similar to user's purchase history.
        """
        recommendations: Dict[int, ProductRecommendation] = {}
        
        orders_result = await self.db.execute(
            select(models.Product)
            .join(models.OrderItem, models.Product.id == models.OrderItem.product_id)
            .join(models.Order, models.OrderItem.order_id == models.Order.id)
            .where(models.Order.buyer_id == user_id)
            .distinct()
        )
        user_products = orders_result.scalars().all()
        
        if not user_products:
            user = await self.db.get(models.User, user_id)
            if user and user.district:
                nearby_result = await self.db.execute(
                    select(models.Product)
                    .join(models.User, models.Product.seller_id == models.User.id)
                    .where(
                        and_(
                            models.Product.status == models.ProductStatus.ACTIVE,
                            models.User.district == user.district
                        )
                    )
                    .limit(limit)
                )
                nearby_products = nearby_result.scalars().all()
                
                for product in nearby_products:
                    recommendations[product.id] = ProductRecommendation(
                        product_id=product.id,
                        product=product,
                        score=0.5,
                        recommendation_type="content_based_location"
                    )
            
            return list(recommendations.values())[:limit]
        
        user_categories = {p.category for p in user_products}
        user_subcategories = {p.subcategory for p in user_products if p.subcategory}
        user_price_range = (
            min(p.price for p in user_products),
            max(p.price for p in user_products)
        )
        
        candidate_result = await self.db.execute(
            select(models.Product)
            .options()
            .where(
                and_(
                    models.Product.status == models.ProductStatus.ACTIVE,
                    or_(
                        models.Product.category.in_(user_categories),
                        models.Product.subcategory.in_(user_subcategories) if user_subcategories else False
                    )
                )
            )
            .limit(100)
        )
        candidates = candidate_result.scalars().all()
        
        purchased_ids = {p.id for p in user_products}
        
        for candidate in candidates:
            if candidate.id in purchased_ids:
                continue
            
            max_similarity = 0.0
            for user_product in user_products:
                similarity = await self._calculate_product_similarity(user_product, candidate)
                max_similarity = max(max_similarity, similarity)
            
            quality_boost = (candidate.quality_rating / 5.0) * 0.2 if candidate.quality_rating > 0 else 0
            
            final_score = max_similarity + quality_boost
            
            if final_score > 0:
                recommendations[candidate.id] = ProductRecommendation(
                    product_id=candidate.id,
                    product=candidate,
                    score=final_score,
                    recommendation_type="content_based"
                )
        
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x.score,
            reverse=True
        )
        
        return sorted_recs[:limit * 2]
    
    async def _knowledge_graph_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """
        Use knowledge graph traversal for recommendations.
        Follow relationships: User -> Preference -> Category -> Products
        """
        graph = await self._get_or_build_graph()
        recommendations: Dict[int, ProductRecommendation] = {}
        
        user_prefs = graph.user_to_preferences.get(user_id, {})
        user_products = graph.user_to_products.get(user_id, set())
        
        if user_prefs:
            for category, pref_weight in user_prefs.items():
                category_products = graph.category_to_products.get(category, set())
                
                for product_id in category_products:
                    if product_id in user_products:
                        continue
                    
                    if product_id not in self._product_cache:
                        continue
                    
                    product = self._product_cache[product_id]
                    score = pref_weight * 0.5
                    
                    if product.quality_rating > 0:
                        score *= (1 + product.quality_rating / 10)
                    
                    if product_id in recommendations:
                        recommendations[product_id].score += score
                    else:
                        recommendations[product_id] = ProductRecommendation(
                            product_id=product_id,
                            product=product,
                            score=score,
                            recommendation_type="knowledge_graph_preference"
                        )
        
        if not user_prefs and user_products:
            related_categories: Dict[str, int] = defaultdict(int)
            
            for product_id in user_products:
                category = graph.product_to_category.get(product_id)
                if category:
                    related_categories[category] += 1
            
            for category, count in related_categories.items():
                category_products = graph.category_to_products.get(category, set())
                
                for product_id in category_products:
                    if product_id in user_products:
                        continue
                    
                    if product_id not in self._product_cache:
                        continue
                    
                    product = self._product_cache[product_id]
                    score = (count / len(user_products)) * 0.5
                    
                    if product_id in recommendations:
                        recommendations[product_id].score += score
                    else:
                        recommendations[product_id] = ProductRecommendation(
                            product_id=product_id,
                            product=product,
                            score=score,
                            recommendation_type="knowledge_graph_traversal"
                        )
        
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x.score,
            reverse=True
        )
        
        return sorted_recs[:limit * 2]
    
    async def _get_cold_start_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """
        Handle new users with no history using popularity and location.
        """
        recommendations: List[ProductRecommendation] = []
        
        user = await self.db.get(models.User, user_id)
        
        if user and user.district:
            popular_result = await self.db.execute(
                select(models.Product)
                .join(models.User, models.Product.seller_id == models.User.id)
                .where(
                    and_(
                        models.Product.status == models.ProductStatus.ACTIVE,
                        models.User.district == user.district,
                        models.Product.quality_rating > 0
                    )
                )
                .order_by(desc(models.Product.quality_rating))
                .limit(limit)
            )
            products = popular_result.scalars().all()
            
            for product in products:
                self._product_cache[product.id] = product
                recommendations.append(ProductRecommendation(
                    product_id=product.id,
                    product=product,
                    score=0.5 + (product.quality_rating / 10),
                    recommendation_type="cold_start_location"
                ))
        
        if len(recommendations) < limit:
            featured_result = await self.db.execute(
                select(models.Product)
                .where(
                    and_(
                        models.Product.status == models.ProductStatus.ACTIVE,
                        models.Product.is_featured == True
                    )
                )
                .order_by(desc(models.Product.quality_rating))
                .limit(limit - len(recommendations))
            )
            featured = featured_result.scalars().all()
            
            for product in featured:
                if product.id not in [r.product_id for r in recommendations]:
                    self._product_cache[product.id] = product
                    recommendations.append(ProductRecommendation(
                        product_id=product.id,
                        product=product,
                        score=0.4 + (product.quality_rating / 10),
                        recommendation_type="cold_start_featured"
                    ))
        
        return recommendations
    
    async def get_recommendations_for_user(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """
        Get personalized product recommendations for a user.
        
        Combines multiple recommendation strategies:
        1. Collaborative filtering (40% weight)
        2. Content-based filtering (30% weight)
        3. Knowledge graph traversal (30% weight)
        
        All recommendations are weighted by seller trust score.
        
        Args:
            user_id: The user ID to get recommendations for
            limit: Maximum number of recommendations to return
        
        Returns:
            List of ProductRecommendation objects sorted by trust-weighted score
        """
        all_recommendations: Dict[int, ProductRecommendation] = {}
        
        user = await self.db.get(models.User, user_id)
        if not user:
            return []
        
        user_vectors = await self._build_user_vectors()
        is_new_user = user_id not in user_vectors or len(user_vectors[user_id]) == 0
        
        if is_new_user:
            cold_start_recs = await self._get_cold_start_recommendations(user_id, limit * 2)
            for rec in cold_start_recs:
                all_recommendations[rec.product_id] = rec
            
            return (await self._apply_trust_weighting(list(all_recommendations.values())))[:limit]
        
        purchased_products = await self._get_user_purchased_products(user_id)
        
        collab_recs = await self._collaborative_filtering(user_id, limit)
        for rec in collab_recs:
            if rec.product_id not in purchased_products:
                if rec.product_id in all_recommendations:
                    all_recommendations[rec.product_id].score += rec.score * 0.4
                else:
                    rec.score *= 0.4
                    all_recommendations[rec.product_id] = rec
        
        content_recs = await self._content_based_filtering(user_id, limit)
        for rec in content_recs:
            if rec.product_id not in purchased_products:
                if rec.product_id in all_recommendations:
                    all_recommendations[rec.product_id].score += rec.score * 0.3
                else:
                    rec.score *= 0.3
                    all_recommendations[rec.product_id] = rec
        
        graph_recs = await self._knowledge_graph_recommendations(user_id, limit)
        for rec in graph_recs:
            if rec.product_id not in purchased_products:
                if rec.product_id in all_recommendations:
                    all_recommendations[rec.product_id].score += rec.score * 0.3
                else:
                    rec.score *= 0.3
                    all_recommendations[rec.product_id] = rec
        
        final_recommendations = await self._apply_trust_weighting(
            list(all_recommendations.values())
        )
        
        return final_recommendations[:limit]
    
    async def get_similar_products(
        self,
        product_id: int,
        limit: int = 5
    ) -> List[ProductRecommendation]:
        """
        Get products similar to a given product.
        
        Uses content-based similarity with trust weighting.
        
        Args:
            product_id: The product ID to find similar products for
            limit: Maximum number of similar products to return
        
        Returns:
            List of ProductRecommendation objects for similar products
        """
        target_product = await self.db.get(models.Product, product_id)
        
        if not target_product:
            return []
        
        if target_product.seller_id:
            seller = await self.db.get(models.User, target_product.seller_id)
            if seller:
                target_product.seller = seller
        
        candidate_result = await self.db.execute(
            select(models.Product)
            .where(
                and_(
                    models.Product.status == models.ProductStatus.ACTIVE,
                    models.Product.id != product_id,
                    or_(
                        models.Product.category == target_product.category,
                        models.Product.subcategory == target_product.subcategory if target_product.subcategory else False
                    )
                )
            )
            .limit(50)
        )
        candidates = candidate_result.scalars().all()
        
        recommendations: List[ProductRecommendation] = []
        
        for candidate in candidates:
            if candidate.seller_id:
                seller = await self.db.get(models.User, candidate.seller_id)
                if seller:
                    candidate.seller = seller
            
            similarity = await self._calculate_product_similarity(target_product, candidate)
            
            quality_weight = (candidate.quality_rating / 5.0) * 0.1 if candidate.quality_rating > 0 else 0
            
            final_score = similarity + quality_weight
            
            if final_score > 0.1:
                recommendations.append(ProductRecommendation(
                    product_id=candidate.id,
                    product=candidate,
                    score=final_score,
                    recommendation_type="similar_product"
                ))
        
        recommendations = await self._apply_trust_weighting(recommendations)
        
        return recommendations[:limit]
    
    async def get_recommended_shgs(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[SHGRecommendation]:
        """
        Get recommended SHGs for a user to follow.
        
        Based on:
        - Similar users' followed SHGs
        - Category preferences matching SHG products
        - Trust scores
        
        Args:
            user_id: The user ID to get SHG recommendations for
            limit: Maximum number of SHG recommendations to return
        
        Returns:
            List of SHGRecommendation objects sorted by score
        """
        recommendations: Dict[int, SHGRecommendation] = {}
        
        user = await self.db.get(models.User, user_id)
        if not user:
            return []
        
        interacted_shgs = await self._get_user_interacted_shgs(user_id)
        
        similar_users = await self._find_similar_users(user_id, min_similarity=0.05)
        
        for similar_user_id, similarity in similar_users:
            similar_shgs = await self._get_user_interacted_shgs(similar_user_id)
            
            for shg_id in similar_shgs:
                if shg_id in interacted_shgs:
                    continue
                
                if shg_id in recommendations:
                    recommendations[shg_id].score += similarity
                else:
                    shg = await self.db.get(models.User, shg_id)
                    if shg:
                        recommendations[shg_id] = SHGRecommendation(
                            shg_id=shg_id,
                            shg=shg,
                            score=similarity,
                            recommendation_reason="Similar users interact with this SHG",
                            trust_score=shg.trust_score
                        )
        
        user_products_result = await self.db.execute(
            select(models.Product.category)
            .join(models.OrderItem, models.Product.id == models.OrderItem.product_id)
            .join(models.Order, models.OrderItem.order_id == models.Order.id)
            .where(models.Order.buyer_id == user_id)
            .distinct()
        )
        user_categories = [row[0] for row in user_products_result]
        
        if user_categories:
            category_shgs_result = await self.db.execute(
                select(models.User)
                .join(models.Product, models.User.id == models.Product.seller_id)
                .where(
                    and_(
                        models.Product.category.in_(user_categories),
                        models.Product.status == models.ProductStatus.ACTIVE,
                        models.User.id.notin_(interacted_shgs)
                    )
                )
                .distinct()
            )
            category_shgs = category_shgs_result.scalars().all()
            
            for shg in category_shgs:
                if shg.id in recommendations:
                    recommendations[shg.id].score += 0.3
                    recommendations[shg.id].recommendation_reason = "Multiple matching factors"
                else:
                    recommendations[shg.id] = SHGRecommendation(
                        shg_id=shg.id,
                        shg=shg,
                        score=0.3,
                        recommendation_reason="Sells products in your preferred categories",
                        trust_score=shg.trust_score
                    )
        
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x.score * (1 + x.trust_score / 100),
            reverse=True
        )
        
        return sorted_recs[:limit]
    
    async def get_trending_products(
        self,
        district: str,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """
        Get trending products in a specific district.
        
        Trending is determined by:
        - Recent order volume (last 30 days)
        - Product quality rating
        - Seller trust score
        
        Args:
            district: The district to get trending products for
            limit: Maximum number of trending products to return
        
        Returns:
            List of ProductRecommendation objects for trending products
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        trending_query = (
            select(
                models.Product,
                func.count(models.OrderItem.id).label("order_count"),
                func.sum(models.OrderItem.quantity).label("total_quantity")
            )
            .join(models.OrderItem, models.Product.id == models.OrderItem.product_id)
            .join(models.Order, models.OrderItem.order_id == models.Order.id)
            .join(models.User, models.Product.seller_id == models.User.id)
            .where(
                and_(
                    models.Product.status == models.ProductStatus.ACTIVE,
                    models.User.district == district,
                    models.Order.created_at >= thirty_days_ago,
                    models.Order.order_status.in_([
                        models.OrderStatus.DELIVERED,
                        models.OrderStatus.CONFIRMED,
                        models.OrderStatus.SHIPPED
                    ])
                )
            )
            .group_by(models.Product.id)
            .order_by(desc("order_count"))
            .limit(limit * 2)
        )
        
        result = await self.db.execute(trending_query)
        trending_data = result.all()
        
        recommendations: List[ProductRecommendation] = []
        
        for product, order_count, total_quantity in trending_data:
            if product.seller_id:
                seller = await self.db.get(models.User, product.seller_id)
                if seller:
                    product.seller = seller
            
            order_score = min(order_count / 10.0, 1.0)
            quantity_score = min((total_quantity or 0) / 50.0, 1.0)
            quality_score = product.quality_rating / 5.0 if product.quality_rating > 0 else 0.5
            
            final_score = (order_score * 0.4) + (quantity_score * 0.3) + (quality_score * 0.3)
            
            recommendations.append(ProductRecommendation(
                product_id=product.id,
                product=product,
                score=final_score,
                recommendation_type="trending"
            ))
        
        recommendations = await self._apply_trust_weighting(recommendations)
        
        if len(recommendations) < limit:
            popular_result = await self.db.execute(
                select(models.Product)
                .join(models.User, models.Product.seller_id == models.User.id)
                .where(
                    and_(
                        models.Product.status == models.ProductStatus.ACTIVE,
                        models.User.district == district,
                        models.Product.quality_rating > 3.0
                    )
                )
                .order_by(desc(models.Product.quality_rating))
                .limit(limit - len(recommendations))
            )
            additional_products = popular_result.scalars().all()
            
            existing_ids = {r.product_id for r in recommendations}
            
            for product in additional_products:
                if product.id in existing_ids:
                    continue
                
                if product.seller_id:
                    seller = await self.db.get(models.User, product.seller_id)
                    if seller:
                        product.seller = seller
                
                recommendations.append(ProductRecommendation(
                    product_id=product.id,
                    product=product,
                    score=0.4 + (product.quality_rating / 10),
                    recommendation_type="trending_popular"
                ))
        
        return recommendations[:limit]
    
    async def refresh_graph(self) -> None:
        """
        Force rebuild of the knowledge graph.
        Call this when significant data changes occur.
        """
        self._graph = None
        self._user_vectors = {}
        self._product_cache = {}
        await self._build_knowledge_graph()
    
    async def get_recommendation_explanation(
        self,
        user_id: int,
        product_id: int
    ) -> Dict[str, any]:
        """
        Get explanation for why a product was recommended to a user.
        
        Args:
            user_id: The user ID
            product_id: The recommended product ID
        
        Returns:
            Dictionary with explanation details
        """
        explanation = {
            "product_id": product_id,
            "user_id": user_id,
            "factors": [],
            "overall_score": 0.0
        }
        
        product = await self.db.get(models.Product, product_id)
        if not product:
            return explanation
        
        user = await self.db.get(models.User, user_id)
        if not user:
            return explanation
        
        user_vectors = await self._build_user_vectors()
        if user_id in user_vectors:
            user_products = user_vectors[user_id]
            
            similar_users = await self._find_similar_users(user_id)
            users_with_product = [
                (uid, sim) for uid, sim in similar_users
                if product_id in user_vectors.get(uid, {})
            ]
            
            if users_with_product:
                explanation["factors"].append({
                    "type": "collaborative_filtering",
                    "description": f"{len(users_with_product)} similar users purchased this product",
                    "weight": sum(sim for _, sim in users_with_product) / len(users_with_product)
                })
        
        orders_result = await self.db.execute(
            select(models.Product)
            .join(models.OrderItem, models.Product.id == models.OrderItem.product_id)
            .join(models.Order, models.OrderItem.order_id == models.Order.id)
            .where(models.Order.buyer_id == user_id)
            .distinct()
        )
        user_purchased = orders_result.scalars().all()
        
        if user_purchased:
            max_similarity = 0.0
            for purchased in user_purchased:
                similarity = await self._calculate_product_similarity(purchased, product)
                max_similarity = max(max_similarity, similarity)
            
            if max_similarity > 0.3:
                explanation["factors"].append({
                    "type": "content_similarity",
                    "description": f"Similar to products you've purchased (score: {max_similarity:.2f})",
                    "weight": max_similarity
                })
        
        if product.category:
            category_count = sum(
                1 for p in user_purchased if p.category == product.category
            )
            if category_count > 0:
                explanation["factors"].append({
                    "type": "category_preference",
                    "description": f"You've purchased {category_count} products in '{product.category}' category",
                    "weight": 0.3
                })
        
        if product.seller_id:
            seller = await self.db.get(models.User, product.seller_id)
            if seller:
                explanation["factors"].append({
                    "type": "trust_score",
                    "description": f"Seller trust score: {seller.trust_score:.1f}",
                    "weight": seller.trust_score / 100
                })
        
        explanation["overall_score"] = sum(
            f["weight"] for f in explanation["factors"]
        ) / len(explanation["factors"]) if explanation["factors"] else 0
        
        return explanation
