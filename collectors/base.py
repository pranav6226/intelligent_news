from typing import List, Dict, Any

class BaseNewsCollector:
    def fetch(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch news articles for a given company.
        Args:
            company: dict with keys 'ticker', 'name', 'aliases'
        Returns:
            List of articles, each as dict with keys:
                - title
                - url
                - published (datetime or string)
                - summary
                - source
        """
        raise NotImplementedError 