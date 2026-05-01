import numpy as np


class LinUCBRecommender:
    def __init__(self, n_arms: int = 5, context_dim: int = 7, alpha: float = 1.0) -> None:
        self.n_arms = n_arms
        self.context_dim = context_dim
        self.alpha = alpha
        self.A = [np.identity(context_dim) for _ in range(n_arms)]
        self.b = [np.zeros(context_dim) for _ in range(n_arms)]

    def recommend(self, context: np.ndarray, top_k: int = 3) -> tuple[list[int], list[float]]:
        scores: list[float] = []
        for arm in range(self.n_arms):
            theta = np.linalg.solve(self.A[arm], self.b[arm])
            uncertainty = self.alpha * np.sqrt(
                context @ np.linalg.solve(self.A[arm], context)
            )
            scores.append(float(theta @ context + uncertainty))

        ranked = np.argsort(scores)[::-1]
        top_indices = [int(index) for index in ranked[:top_k]]
        return top_indices, [float(scores[index]) for index in top_indices]

    def update(self, arm: int, context: np.ndarray, reward: float) -> None:
        self.A[arm] += np.outer(context, context)
        self.b[arm] += reward * context
