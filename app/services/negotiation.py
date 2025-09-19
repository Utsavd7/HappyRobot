from typing import Dict, Any
from app.models.load import Load

class NegotiationService:
    """Handle price negotiation logic"""
    
    @staticmethod
    def evaluate_offer(load: Load, offered_rate: float, negotiation_round: int) -> Dict[str, Any]:
        """
        Evaluate a carrier's price offer
        Returns decision on whether to accept, counter, or transfer
        """
        base_rate = load.loadboard_rate
        min_acceptable_rate = base_rate * 0.85  # 15% below listed rate
        
        # Check negotiation rounds
        if negotiation_round > 3:
            return {
                "action": "transfer_to_rep",
                "accepted": False,
                "reason": "Maximum negotiation rounds exceeded",
                "message": "I'll need to transfer you to a sales representative for further assistance."
            }
        
        # Accept if within 5% of asking price
        if offered_rate >= base_rate * 0.95:
            return {
                "action": "accept",
                "accepted": True,
                "final_rate": offered_rate,
                "message": f"Great! I can accept your rate of ${offered_rate:.2f} for this load."
            }
        
        # Counter offer if rate is reasonable but low
        elif offered_rate >= min_acceptable_rate:
            # Calculate counter offer (meet halfway between offer and base rate)
            counter_rate = offered_rate + ((base_rate - offered_rate) * 0.3)
            return {
                "action": "counter_offer",
                "accepted": False,
                "counter_rate": round(counter_rate, 2),
                "message": f"I appreciate your offer. I can go as low as ${counter_rate:.2f} for this load. Would that work for you?"
            }
        
        # Decline if too low
        else:
            if negotiation_round < 2:
                return {
                    "action": "decline_continue",
                    "accepted": False,
                    "min_rate": round(min_acceptable_rate, 2),
                    "message": f"I understand you're looking for the best rate. The lowest I can offer for this load is ${min_acceptable_rate:.2f}. Would you like to reconsider?"
                }
            else:
                return {
                    "action": "transfer_to_rep",
                    "accepted": False,
                    "reason": "Rate too low after multiple attempts",
                    "message": "I see we're having difficulty agreeing on a rate. Let me transfer you to a sales representative who may have more flexibility."
                }

negotiation_service = NegotiationService()