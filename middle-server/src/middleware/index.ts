import NonceMiddleware, { NonceConfig } from './nonce';

// Comprehensive export of nonce middleware functionality
export {
  NonceMiddleware,  // Class for custom configurations
  NonceConfig       // Configuration interface
};

// Default middleware instance
const defaultNonceMiddleware = NonceMiddleware;

// Expose core methods for easy use
export const nonceHandler = defaultNonceMiddleware.handler;
export const generateNonceHeader = defaultNonceMiddleware.generateNonceHeader;
export const getNonceStoreStats = defaultNonceMiddleware.getNonceStoreStats;

export default defaultNonceMiddleware;