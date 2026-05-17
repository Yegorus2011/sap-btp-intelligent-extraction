import asyncio
import random
import json

# =====================================================================
# 1. Менеджер авторизації (Security Layer)
# =====================================================================
class SAPClientManager: 
    def __init__(self, service_key):  
        self.service_key = service_key 
        self.token = None 

    def get_token(self):  
        self.token = "active_oauth_token_from_btp"
        return self.token

# =====================================================================
# 2. Трубопровід екстракції (AI/Processing Layer)
# =====================================================================
class ExtractionPipeline: 
    def __init__(self, client_manager):
        self.client = client_manager
    
    async def run_extraction(self, document_path): 
        token = self.client.get_token()
        # Симуляція затримки мережевого запиту до SAP AI Core
        await asyncio.sleep(1) 
        random_confidence = round(random.uniform(0.70, 0.99), 2)
        return {"equipment_id": "TR-450", "confidence": random_confidence}

# =====================================================================
# 3. Двигун валідації (Business Logic Layer)
# =====================================================================
class ValidationEngine: 
    def __init__(self, threshold=0.90):
        self.threshold = threshold
    
    def validate(self, result):
        # ERR-003 Fix: Безпечне вилучення через .get()
        confidence = result.get('confidence', 0)
        if confidence >= self.threshold:
            return "VALIDATED_AUTOMATICALLY"
        return "PENDING_MANUAL_REVIEW"

# =====================================================================
# 4. Інтеграційний шлюз (Integration Layer)
# =====================================================================
class IntegrationGateway:
    def __init__(self, pipeline, validator):
        self.pipeline = pipeline
        self.validator = validator

    async def process_rest_request(self, payload_json):
        try:
            # Десеріалізація вхідного JSON-пакета (Payload)
            request_data = json.loads(payload_json)
            
            # ERR-004 Simulation: Контроль обов'язкових полів на вході шлюзу
            if "file_path" not in request_data:
                raise ValueError("Missing 'file_path' in request payload")

            doc_path = request_data["file_path"]
            
            # Оркестрація внутрішніх сервісів обробки
            raw_result = await self.pipeline.run_extraction(doc_path)
            status = self.validator.validate(raw_result)
            
            # Формування успішної JSON-відповіді (Response Contract)
            response = {
                "status": "success",
                "extracted_data": {
                    "equipment_id": raw_result["equipment_id"],
                    "engine": "SAP_DOX_CORE_V2"
                },
                "confidence": raw_result["confidence"],
                "decision": status
            }
            return json.dumps(response, indent=4, ensure_ascii=False)

        except ValueError as ve:
            # Специфічний вивід для передбачуваної помилки валідації контракту
            error_response = {
                "status": "error",
                "code": "ERR-004",
                "message": str(ve)
            }
            return json.dumps(error_response, indent=4)
        except Exception as e:
            # Загальний перехоплювач непередбачуваних збоїв системи
            return json.dumps({"status": "error", "message": f"Unexpected system error: {str(e)}"}, indent=4)

# =====================================================================
# 5. Головна функція (Orchestrator / Тестове середовище)
# =====================================================================
async def main(): 
    print("-" * 60)
    print("СИСТЕМА ІНТЕЛЕКТУАЛЬНОЇ ОБРОБКИ ДОКУМЕНТІВ (REST API SIM)")
    print("-" * 60)
    
    # Ініціалізація інфраструктурних компонентів
    auth = SAPClientManager(service_key="key.json")
    pipeline = ExtractionPipeline(auth)
    validator = ValidationEngine(threshold=0.92) # Встановлюємо кафедральний поріг
    
    # Створення архітектурного шлюзу
    gateway = IntegrationGateway(pipeline, validator)
    
    # -----------------------------------------------------------------
    # ТЕСТ 1: Симуляція успішного REST-запиту
    # -----------------------------------------------------------------
    print("\n[ТЕСТ 1] Надсилання валідного JSON-запиту:")
    valid_payload = '{"file_path": "transformer_passport.pdf", "doc_type": "technical_passport"}'
    response_1 = await gateway.process_rest_request(valid_payload)
    print(response_1)
    
    # -----------------------------------------------------------------
    # ТЕСТ 2: Симуляція помилки (ERR-004) для перевірки захисту
    # -----------------------------------------------------------------
    print("\n[ТЕСТ 2] Симуляція помилки (відсутній file_path):")
    invalid_payload = '{"doc_type": "technical_passport"}'
    response_2 = await gateway.process_rest_request(invalid_payload)
    print(response_2)

if __name__ == "__main__":
    asyncio.run(main())