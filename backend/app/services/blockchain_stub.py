"""
Blockchain Stub Service for Trust Events

This is a STUB implementation for demo purposes only.
In production, this would connect to an actual blockchain network
(e.g., Ethereum, Hyperledger, or a custom distributed ledger).

This implementation provides:
- Simple hash-chained blockchain for immutable event logging
- Trust event tracking for users
- Chain integrity verification
- Audit trail capabilities

WARNING: This is NOT a real blockchain - it's a local in-memory
implementation for demonstration. Data is not persisted or distributed.
"""

import hashlib
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class EventType(str, Enum):
    TRUST_SCORE_CHANGE = "TRUST_SCORE_CHANGE"
    COIN_TRANSACTION = "COIN_TRANSACTION"
    ORDER_COMPLETE = "ORDER_COMPLETE"
    BADGE_CHANGE = "BADGE_CHANGE"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    AUDIT_LOG = "AUDIT_LOG"


@dataclass
class Block:
    index: int
    timestamp: float
    data: Dict[str, Any]
    previous_hash: str
    hash: str = ""
    nonce: int = 0

    def calculate_hash(self) -> str:
        block_content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_content, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TrustEventBlockchain:
    _instance: Optional['TrustEventBlockchain'] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls) -> 'TrustEventBlockchain':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.chain: List[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis_block = Block(
            index=0,
            timestamp=0.0,
            data={"event": "GENESIS", "message": "Trust Event Blockchain Genesis Block"},
            previous_hash="0"
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)

    @classmethod
    async def get_instance(cls) -> 'TrustEventBlockchain':
        async with cls._lock:
            return cls()

    async def add_trust_event(
        self,
        user_id: str,
        event_type: EventType,
        event_data: Dict[str, Any]
    ) -> int:
        async with self._lock:
            previous_block = self.chain[-1]
            new_index = previous_block.index + 1
            timestamp = datetime.utcnow().timestamp()

            data = {
                "user_id": user_id,
                "event_type": event_type.value,
                "event_data": event_data,
                "recorded_at": datetime.utcnow().isoformat()
            }

            new_block = Block(
                index=new_index,
                timestamp=timestamp,
                data=data,
                previous_hash=previous_block.hash,
                nonce=0
            )
            new_block.hash = new_block.calculate_hash()
            self.chain.append(new_block)
            return new_block.index

    async def get_user_events(self, user_id: str) -> List[Dict[str, Any]]:
        async with self._lock:
            return [
                block.to_dict()
                for block in self.chain
                if block.index > 0 and block.data.get("user_id") == user_id
            ]

    async def get_chain_stats(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "chain_length": len(self.chain),
                "last_block_index": self.chain[-1].index if self.chain else 0,
                "last_hash": self.chain[-1].hash if self.chain else None,
                "genesis_hash": self.chain[0].hash if self.chain else None,
                "created_at": datetime.fromtimestamp(self.chain[0].timestamp).isoformat() if self.chain else None,
                "last_updated": datetime.fromtimestamp(self.chain[-1].timestamp).isoformat() if self.chain else None
            }

    async def verify_chain_integrity(self) -> bool:
        async with self._lock:
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]

                if current_block.hash != current_block.calculate_hash():
                    return False

                if current_block.previous_hash != previous_block.hash:
                    return False

            return True


_blockchain_instance: Optional[TrustEventBlockchain] = None
_blockchain_lock = asyncio.Lock()


async def _get_blockchain() -> TrustEventBlockchain:
    global _blockchain_instance
    if _blockchain_instance is None:
        async with _blockchain_lock:
            if _blockchain_instance is None:
                _blockchain_instance = TrustEventBlockchain()
    return _blockchain_instance


async def log_trust_event(
    user_id: str,
    event_type: EventType,
    data: Dict[str, Any]
) -> int:
    blockchain = await _get_blockchain()
    return await blockchain.add_trust_event(user_id, event_type, data)


async def get_audit_trail(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    blockchain = await _get_blockchain()
    all_events = await blockchain.get_user_events(user_id)

    filtered_events = []
    for event in all_events:
        event_time_str = event.get("data", {}).get("recorded_at")
        if not event_time_str:
            continue

        try:
            event_time = datetime.fromisoformat(event_time_str)
        except (ValueError, TypeError):
            continue

        if start_date and event_time < start_date:
            continue
        if end_date and event_time > end_date:
            continue

        filtered_events.append(event)

    return filtered_events


async def verify_user_history(user_id: str) -> Dict[str, Any]:
    blockchain = await _get_blockchain()
    chain_valid = await blockchain.verify_chain_integrity()
    user_events = await blockchain.get_user_events(user_id)

    event_count = len(user_events)
    event_types = {}
    for event in user_events:
        event_type = event.get("data", {}).get("event_type", "UNKNOWN")
        event_types[event_type] = event_types.get(event_type, 0) + 1

    return {
        "user_id": user_id,
        "chain_valid": chain_valid,
        "event_count": event_count,
        "event_type_breakdown": event_types,
        "verified_at": datetime.utcnow().isoformat()
    }


async def export_blockchain_data() -> Dict[str, Any]:
    blockchain = await _get_blockchain()
    stats = await blockchain.get_chain_stats()
    chain_valid = await blockchain.verify_chain_integrity()

    async with blockchain._lock:
        chain_data = [block.to_dict() for block in blockchain.chain]

    return {
        "stats": stats,
        "chain_valid": chain_valid,
        "chain": chain_data,
        "exported_at": datetime.utcnow().isoformat()
    }
