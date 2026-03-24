import { useState, useEffect } from 'react';
import { useRealTime } from './RealTimeProvider';
import { Clock, Package, Truck, CheckCircle, AlertCircle } from 'lucide-react';

const STATUS_CONFIG = {
  pending: {
    label: 'Pending',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    icon: Clock,
    pulseColor: 'bg-yellow-400',
  },
  processing: {
    label: 'Processing',
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    icon: Package,
    pulseColor: 'bg-blue-400',
  },
  shipped: {
    label: 'Shipped',
    color: 'bg-purple-100 text-purple-800 border-purple-300',
    icon: Truck,
    pulseColor: 'bg-purple-400',
  },
  delivered: {
    label: 'Delivered',
    color: 'bg-green-100 text-green-800 border-green-300',
    icon: CheckCircle,
    pulseColor: null,
  },
  cancelled: {
    label: 'Cancelled',
    color: 'bg-red-100 text-red-800 border-red-300',
    icon: AlertCircle,
    pulseColor: null,
  },
};

const ACTIVE_STATUSES = ['pending', 'processing', 'shipped'];

const OrderStatusBadge = ({ orderId, initialStatus }) => {
  const [status, setStatus] = useState(initialStatus || 'pending');
  const { connected, orders, subscribe } = useRealTime();

  useEffect(() => {
    if (!connected) return;

    const unsubscribe = subscribe(`order:${orderId}`, (data) => {
      if (data.status) {
        setStatus(data.status);
      }
    });

    return unsubscribe;
  }, [connected, orderId, subscribe]);

  useEffect(() => {
    const orderFromList = orders.find((o) => o.id === orderId);
    if (orderFromList?.status) {
      setStatus(orderFromList.status);
    }
  }, [orders, orderId]);

  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  const Icon = config.icon;
  const isActive = ACTIVE_STATUSES.includes(status);

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${config.color} transition-all duration-300`}
    >
      {isActive && (
        <span className="relative flex h-2 w-2">
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.pulseColor} opacity-75`}
          ></span>
          <span
            className={`relative inline-flex rounded-full h-2 w-2 ${config.pulseColor}`}
          ></span>
        </span>
      )}
      <Icon size={14} className={isActive ? 'animate-pulse' : ''} />
      <span className="text-xs font-semibold">{config.label}</span>
      {connected && (
        <span className="ml-1 w-1.5 h-1.5 bg-green-500 rounded-full" title="Live" />
      )}
    </div>
  );
};

export default OrderStatusBadge;
