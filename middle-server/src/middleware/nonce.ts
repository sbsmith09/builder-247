import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

// Comprehensive configuration interface for nonce middleware
export interface NonceConfig {
  headerName?: string;         // Custom header for nonce
  maxNonceAge?: number;        // Nonce expiration time
  nonceLength?: number;        // Nonce byte length
  excludedMethods?: string[];  // Methods to skip nonce validation
  maxNonceStore?: number;      // Maximum number of stored nonces
}

export class NonceMiddleware {
  private config: Required<NonceConfig>;
  private nonceStore: Map<string, number>;

  constructor(config: NonceConfig = {}) {
    // Comprehensive default configuration
    this.config = {
      headerName: 'X-Nonce',
      maxNonceAge: 5 * 60 * 1000,   // 5 minutes
      nonceLength: 32,              // 32 bytes = 64 hex characters
      excludedMethods: ['GET', 'HEAD', 'OPTIONS'],
      maxNonceStore: 1000,          // Prevent memory exhaustion
      ...config
    };

    this.nonceStore = new Map();
  }

  /**
   * Generate a cryptographically secure nonce
   * @returns {string} Hex-encoded nonce
   */
  private generateNonce(): string {
    return crypto.randomBytes(this.config.nonceLength).toString('hex');
  }

  /**
   * Remove expired and excess nonces from the store
   */
  private cleanupNonceStore(): void {
    const now = Date.now();
    const expiredNonces: string[] = [];

    // Find expired nonces
    for (const [nonce, timestamp] of this.nonceStore.entries()) {
      if (now - timestamp > this.config.maxNonceAge) {
        expiredNonces.push(nonce);
      }
    }

    // Remove expired nonces
    expiredNonces.forEach(nonce => this.nonceStore.delete(nonce));

    // Trim store if it exceeds max size
    if (this.nonceStore.size > this.config.maxNonceStore) {
      const oldestNonces = Array.from(this.nonceStore.entries())
        .sort((a, b) => a[1] - b[1])
        .slice(0, this.nonceStore.size - this.config.maxNonceStore);

      oldestNonces.forEach(([nonce]) => this.nonceStore.delete(nonce));
    }
  }

  /**
   * Validate and consume a nonce
   * @param nonce Nonce to validate
   * @returns {boolean} Whether the nonce is valid
   */
  private validateAndConsumeNonce(nonce: string): boolean {
    if (!nonce) return false;

    const timestamp = this.nonceStore.get(nonce);
    if (!timestamp) return false;

    const now = Date.now();
    if (now - timestamp > this.config.maxNonceAge) return false;

    // Remove the nonce after validation to prevent replay
    this.nonceStore.delete(nonce);
    return true;
  }

  /**
   * Middleware to validate nonces for protected routes
   */
  public handler = (req: Request, res: Response, next: NextFunction): void => {
    try {
      // Clean up the nonce store
      this.cleanupNonceStore();

      // Skip nonce validation for excluded methods
      if (this.config.excludedMethods.includes(req.method)) {
        return next();
      }

      // Retrieve nonce from request header
      const clientNonce = req.get(this.config.headerName);

      // Validate nonce
      if (!this.validateAndConsumeNonce(clientNonce)) {
        return res.status(403).json({
          error: 'Nonce Validation Failed',
          message: 'Invalid, expired, or already used nonce',
          details: {
            method: req.method,
            path: req.path
          }
        });
      }

      next();
    } catch (error) {
      // Comprehensive error handling
      res.status(500).json({
        error: 'Nonce Middleware Error',
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        details: {
          method: req.method,
          path: req.path
        }
      });
    }
  }

  /**
   * Generate and inject a new nonce into the response
   */
  public generateNonceHeader = (req: Request, res: Response, next: NextFunction): void => {
    try {
      // Clean up the nonce store before generating a new nonce
      this.cleanupNonceStore();

      // Generate a new unique nonce
      const nonce = this.generateNonce();

      // Store the nonce with current timestamp
      this.nonceStore.set(nonce, Date.now());

      // Set nonce in response header
      res.set(this.config.headerName, nonce);

      next();
    } catch (error) {
      // Fallback error handling
      res.status(500).json({
        error: 'Nonce Generation Failed',
        message: error instanceof Error ? error.message : 'Unable to generate nonce'
      });
    }
  }

  /**
   * Get current nonce store statistics
   */
  public getNonceStoreStats(): { 
    currentSize: number, 
    maxSize: number, 
    oldestNonce?: number 
  } {
    const timestamps = Array.from(this.nonceStore.values());
    return {
      currentSize: this.nonceStore.size,
      maxSize: this.config.maxNonceStore,
      oldestNonce: timestamps.length > 0 ? Math.min(...timestamps) : undefined
    };
  }
}

// Export a default instance with standard configuration
export default new NonceMiddleware();