from app.services.demo_store import DemoStore


class PortfolioMonitorService:
    def __init__(self, store: DemoStore) -> None:
        self.store = store

    def trigger_demo_rescore(self) -> None:
        self.store.trigger_portfolio_rescore()
