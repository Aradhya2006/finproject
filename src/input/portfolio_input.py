class PortfolioInput:
    def __init__(
        self,
        holdings,
        prices,
        holding_values,
        portfolio_value,
        weights,
        assets,
        source,
        detected_holdings=None,
        verified_holdings=None,
    ):
        self.holdings = holdings
        self.prices = prices
        self.holding_values = holding_values
        self.portfolio_value = portfolio_value
        self.weights = weights
        self.assets = assets
        self.source = source
        self.detected_holdings = detected_holdings
        self.verified_holdings = verified_holdings

    def to_dict(self):
        return {
            "holdings": self.holdings,
            "prices": self.prices,
            "holding_values": self.holding_values,
            "portfolio_value": self.portfolio_value,
            "weights": self.weights,
            "assets": self.assets,
            "source": self.source,
            "detected_holdings": self.detected_holdings,
            "verified_holdings": self.verified_holdings,
        }

    def __getitem__(self, key):
        return self.to_dict()[key]