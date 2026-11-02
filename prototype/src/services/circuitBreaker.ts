export enum CircuitBreakerState {
  CLOSED = 0,
  OPEN = 1,
  HALF_OPEN = 2
}

export class CircuitBreaker {
  private state: CircuitBreakerState = CircuitBreakerState.CLOSED;
  private failureCount: number = 0;
  private readonly failureThreshold: number = 5;
  private readonly openTimeoutMs: number = 60000; // 60 seconds
  private lastStateChangeTime: number = Date.now();

  public async execute<T>(action: () => Promise<T>): Promise<T> {
    const now = Date.now();

    if (this.state === CircuitBreakerState.OPEN) {
      if (now - this.lastStateChangeTime > this.openTimeoutMs) {
        this.state = CircuitBreakerState.HALF_OPEN;
        this.lastStateChangeTime = now;
      } else {
        throw new Error('ERR-LOAD-002: Circuit breaker is OPEN. Fast-failing request.');
      }
    }

    try {
      const result = await action();
      if (this.state === CircuitBreakerState.HALF_OPEN) {
        this.state = CircuitBreakerState.CLOSED;
        this.failureCount = 0;
      }
      return result;
    } catch (err) {
      this.failureCount++;
      if (this.failureCount >= this.failureThreshold || this.state === CircuitBreakerState.HALF_OPEN) {
        this.state = CircuitBreakerState.OPEN;
        this.lastStateChangeTime = now;
      }
      throw err;
    }
  }

  public getState(): CircuitBreakerState {
    return this.state;
  }
}
