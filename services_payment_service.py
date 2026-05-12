import requests
import hashlib
import json
import logging
from datetime import datetime
from config import (
    PAYME_MERCHANT_ID, PAYME_API_KEY,
    CLICK_SERVICE_ID, CLICK_MERCHANT_ID, CLICK_API_KEY,
    NEXT_DOC_PRICE_UZS, NEXT_DOC_PRICE_USD
)
from database import save_payment, update_payment_status

logger = logging.getLogger(__name__)

class PaymentService:
    """Handle payment processing with Click.uz and Payme"""
    
    def __init__(self):
        self.click_api_url = "https://api.click.uz/v2"
        self.payme_api_url = "https://checkout.paycom.uz/api"
        
        self.click_merchant_id = CLICK_MERCHANT_ID
        self.click_service_id = CLICK_SERVICE_ID
        self.click_api_key = CLICK_API_KEY
        
        self.payme_merchant_id = PAYME_MERCHANT_ID
        self.payme_api_key = PAYME_API_KEY
    
    # ============ CLICK.UZ METHODS ============
    
    def generate_click_invoice(self, user_id, amount, order_id, currency="UZS"):
        """Generate Click.uz payment link"""
        try:
            # Calculate signature
            sign_string = f"{order_id};{self.click_service_id};{amount};{self.click_api_key}"
            signature = hashlib.md5(sign_string.encode()).hexdigest()
            
            # Create payment link
            payment_url = (
                f"https://click.uz/services/pay?"
                f"service_id={self.click_service_id}"
                f"&merchant_id={self.click_merchant_id}"
                f"&amount={amount}"
                f"&transaction_param={order_id}"
                f"&return_url=https://t.me/akadem_yordamchi_bot"
                f"&merchant_user_id={user_id}"
                f"&sign_string={signature}"
            )
            
            logger.info(f"✅ Click invoice generated for user {user_id}")
            return payment_url
        
        except Exception as e:
            logger.error(f"Error generating Click invoice: {e}")
            return None
    
    def verify_click_payment(self, click_trans_id, merchant_trans_id, amount):
        """Verify Click.uz payment"""
        try:
            url = f"{self.click_api_url}/merchant/transactions/{click_trans_id}/confirm"
            
            sign_string = f"{click_trans_id};{self.click_api_key}"
            signature = hashlib.md5(sign_string.encode()).hexdigest()
            
            headers = {
                "Authorization": f"Bearer {self.click_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "sign_string": signature
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"✅ Click payment verified: {click_trans_id}")
                return True
            else:
                logger.warning(f"❌ Click payment verification failed: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error verifying Click payment: {e}")
            return False
    
    # ============ PAYME METHODS ============
    
    def generate_payme_invoice(self, user_id, amount, order_id, currency="UZS"):
        """Generate Payme payment link"""
        try:
            # Calculate amount in tiyn (smallest unit)
            if currency == "USD":
                # Convert to UZS first (1 USD = ~12800 UZS)
                amount_tiyn = int(amount * 12800 * 100)
            else:
                amount_tiyn = int(amount * 100)
            
            # Create payment link
            payment_url = (
                f"https://checkout.paycom.uz?"
                f"account[user_id]={user_id}"
                f"&amount={amount_tiyn}"
                f"&description=Document+creation+service"
                f"&order_id={order_id}"
                f"&return_url=https://t.me/akadem_yordamchi_bot"
            )
            
            logger.info(f"✅ Payme invoice generated for user {user_id}")
            return payment_url
        
        except Exception as e:
            logger.error(f"Error generating Payme invoice: {e}")
            return None
    
    def verify_payme_payment(self, transaction_id):
        """Verify Payme payment status"""
        try:
            auth_string = f"{self.payme_merchant_id}:{self.payme_api_key}"
            auth_header = requests.auth.HTTPBasicAuth(
                self.payme_merchant_id,
                self.payme_api_key
            )
            
            url = f"{self.payme_api_url}/GetTransaction"
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "CheckTransaction",
                "params": {
                    "id": transaction_id
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                auth=auth_header,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and data["result"].get("state") == 2:  # 2 = completed
                    logger.info(f"✅ Payme payment verified: {transaction_id}")
                    return True
                else:
                    logger.warning(f"❌ Payme payment not completed: {data}")
                    return False
            else:
                logger.warning(f"❌ Payme verification failed: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error verifying Payme payment: {e}")
            return False
    
    # ============ COMMON METHODS ============
    
    def create_payment_record(self, user_id, amount, currency, gateway):
        """Create payment record in database"""
        try:
            payment = save_payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                gateway=gateway,
                status="pending"
            )
            logger.info(f"✅ Payment record created: {payment.id}")
            return payment
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            return None
    
    def complete_payment(self, payment_id, transaction_id, status="success"):
        """Mark payment as completed"""
        try:
            payment = update_payment_status(payment_id, status, transaction_id)
            if payment and status == "success":
                logger.info(f"✅ Payment completed: {payment_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error completing payment: {e}")
            return False
    
    def get_payment_link(self, user_id, amount, currency, gateway, order_id=None):
        """Get payment link for specified gateway"""
        try:
            if order_id is None:
                order_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if gateway == "click":
                return self.generate_click_invoice(user_id, amount, order_id, currency)
            elif gateway == "payme":
                return self.generate_payme_invoice(user_id, amount, order_id, currency)
            else:
                logger.error(f"Unknown gateway: {gateway}")
                return None
        
        except Exception as e:
            logger.error(f"Error getting payment link: {e}")
            return None
    
    def get_default_amount(self, currency="UZS"):
        """Get default payment amount"""
        if currency == "USD":
            return NEXT_DOC_PRICE_USD
        else:
            return NEXT_DOC_PRICE_UZS
    
    # ============ WEBHOOK HANDLERS ============
    
    def handle_click_webhook(self, data):
        """Handle Click.uz webhook"""
        try:
            # Verify signature
            click_trans_id = data.get("click_trans_id")
            merchant_trans_id = data.get("merchant_trans_id")
            amount = data.get("amount")
            sign_string = data.get("sign_string")
            
            # Validate signature
            calculated_sign = hashlib.md5(
                f"{click_trans_id};{self.click_api_key}".encode()
            ).hexdigest()
            
            if calculated_sign != sign_string:
                logger.warning(f"❌ Invalid Click signature")
                return {"error": "Invalid signature"}
            
            # Verify payment
            if self.verify_click_payment(click_trans_id, merchant_trans_id, amount):
                logger.info(f"✅ Click payment confirmed: {click_trans_id}")
                return {"success": True}
            else:
                return {"error": "Payment verification failed"}
        
        except Exception as e:
            logger.error(f"Error handling Click webhook: {e}")
            return {"error": str(e)}
    
    def handle_payme_webhook(self, data):
        """Handle Payme webhook"""
        try:
            transaction_id = data.get("transaction_id")
            
            if self.verify_payme_payment(transaction_id):
                logger.info(f"✅ Payme payment confirmed: {transaction_id}")
                return {"success": True}
            else:
                return {"error": "Payment verification failed"}
        
        except Exception as e:
            logger.error(f"Error handling Payme webhook: {e}")
            return {"error": str(e)}
