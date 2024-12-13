import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests

load_dotenv()

class GPTAssistant:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.endpoint = "https://models.inference.ai.azure.com"
        self.model_name = "gpt-4o-mini"
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_categories",
                    "description": "Get list of product categories from store",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_food",
                    "description": "Get top 5 food from store",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_service",
                    "description": "Get service by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category_name": {
                                "type": "string",
                                "description": "Category name",
                                "example": "Food, Drinks, Laundry, etc"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_restaurants",
                    "description": "Get top N restaurants by service ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_id": {
                                "type": "integer",
                                "description": "Service ID to filter restaurants",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of restaurants to return (default 10)",
                            }
                        },
                        "required": []
                    }
                }
            }
        ]

    def get_categories(self):
        """Get list of product categories from store"""
        response = requests.get("https://huyitshop.online:444/api/v1/categories")
        data = response.json()
        categories = []
        for category in data["result"]:
            # Skip the "Tất cả" category
            if category["categoryName"].lower() != "tất cả":
                categories.append({
                    "name": category["categoryName"],
                    "id": category["categoryId"],
                    "sequence": category["categorySeq"]
                })
        return json.dumps({"categories": categories}, ensure_ascii=False)

    def get_top_food(self):
      """Get top 5 food from store"""
      response = requests.get("https://huyitshop.online:444/api/v1/main-advertisements/top-food")
      data = response.json()
      products = []
      for product in data["result"]:
        products.append({
        "name": product["mainAdvertisementName"],
        "id": product["advertisementId"],
        "price": product["priceRangeLow"],
        "address": product["address"],
        "phoneNumber": product["phoneNumber"],
        "priceRangeLow": product["priceRangeLow"],
        "priceRangeHigh": product["priceRangeHigh"],
        "imageLink": product["mediaList"][0]["url"] if product["mediaList"] else None
        })
      return json.dumps({"products": products}, ensure_ascii=False)

    def get_service(self, category_name: str = ""):
        """Get service by name"""
        response = requests.get(f"https://huyitshop.online:444/api/v1/advertisement-services/category?categoryName={category_name}")
        data = response.json()
        services = []
        for service in data["result"]:
            services.append({
                "name": service["serviceName"],
                "id": service["serviceId"],
                "deliveryAvailable": service["deliveryAvailable"]
            })
        return json.dumps({"services": services}, ensure_ascii=False)

    def get_top_restaurants(self, service_id: int = 0, limit: int = 10):
        """Get top restaurants by service ID"""
        response = requests.get(f"https://huyitshop.online:444/api/v1/main-advertisements/top-restaurants?serviceId={service_id}&limit={limit}")
        data = response.json()
        restaurants = []
        for restaurant in data["result"]:
            restaurants.append({
                "name": restaurant["mainAdvertisementName"],
                "id": restaurant["advertisementId"],
                "serviceId": restaurant["serviceId"],
                "categoryName": restaurant["categoryName"],
                "serviceName": restaurant["serviceName"],
                "address": restaurant["address"],
                "phoneNumber": restaurant["phoneNumber"],
                "priceRangeLow": restaurant["priceRangeLow"],
                "priceRangeHigh": restaurant["priceRangeHigh"],
                "openingHourStart": restaurant["openingHourStart"],
                "openingHourEnd": restaurant["openingHourEnd"],
                "deliveryAvailable": restaurant["deliveryAvailable"],
                "averageRating": restaurant["averageRating"],
                "reviewCount": restaurant["reviewCount"],
                "imageLink": restaurant["mediaList"][0]["url"] if restaurant["mediaList"] else None
            })
        return json.dumps({"restaurants": restaurants}, ensure_ascii=False)

    def process_message(self, user_message: str):
        print(user_message)

        # Check if message is a greeting
        greetings = [
            "xin chào", "hi", "hello", "chào",
            "bạn có thể giúp cho tôi", "bạn có thể giúp tôi",
            "cho tôi hỏi", "tôi cần hỏi", "tôi muốn hỏi",
            "chào bạn", "hey", "có ai không",
            "bạn ơi", "alo", "giúp tôi", "giúp mình",
            "mình cần hỏi", "mình muốn hỏi",
            "chào shop", "shop ơi", "cửa hàng ơi",
            "có thể giúp mình", "cần tư vấn"
        ]
        if any(greeting in user_message.lower() for greeting in greetings):
            return self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Bạn là chatbot AI của dichvuhungngan. Hãy chào đón người dùng một cách thân thiện."},
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": "Xin chào! Tôi là chatbot AI của dichvuhungngan. Tôi có thể giúp gì được cho bạn?"}
                ],
                model=self.model_name,
            )

        # Original system message and logic for non-greeting messages
        messages = [
            {"role": "system", "content": """
          Bạn là chatbot AI của dichvuhungngan. Hãy trả lời với phong cách thân thiện, nhiệt tình và chuyên nghiệp:

          1. Với danh sách món ăn/nhà hàng, hãy hiển thị:
            "Dạ, em xin giới thiệu đến anh/chị những món ăn nổi bật của chúng em ạ:"

            [STT]. [Tên]
            - Giá: [Giá] VNĐ
            - Địa chỉ: [Địa chỉ]
            - Điện thoại: [Số điện thoại]

          2. Với danh sách danh mục/dịch vụ chính, hãy hiển thị:
            "Dạ, em xin phép chia sẻ các dịch vụ hiện có của dichvuhungngan ạ:"

            🏪 DANH SÁCH DỊCH VỤ CHÍNH:

            [STT]. [Tên danh mục] 📍

          3. Với danh sách dịch vụ theo danh mục, hãy hiển thị:
            "Dạ, trong lĩnh vực [Tên danh mục], chúng em có các dịch vụ sau ạ:"

            📌 CÁC DỊCH VỤ [TÊN DANH MỤC]:

            [STT]. [Tên dịch vụ]
            ✅ Giao hàng: [Có/Không]

          4. Các câu mở đầu nên thay đổi đa dạng:
            - "Dạ, em xin phép tư vấn cho anh/chị..."
            - "Em rất vui được chia sẻ với anh/chị..."
            - "Để phục vụ anh/chị tốt nhất, em xin giới thiệu..."
            - "Dạ, em xin gửi đến anh/chị thông tin về..."
            - "Em rất hân hạnh được giới thiệu đến anh/chị..."

          5. Các câu kết thúc nên gợi mở và thân thiện:
            - "Anh/chị quan tâm đến dịch vụ nào trong số này không ạ?"
            - "Em có thể tư vấn chi tiết hơn về bất kỳ dịch vụ nào anh/chị quan tâm ạ"
            - "Nếu anh/chị cần thêm thông tin về dịch vụ nào, em rất sẵn lòng hỗ trợ ạ"
            - "Anh/chị muốn tìm hiểu thêm về dịch vụ nào không ạ?"
            - "Em có thể giúp gì thêm cho anh/chị không ạ?"

          6. Khi không có thông tin:
            "Dạ, em xin lỗi anh/chị. Hiện tại em chưa có thông tin về dịch vụ này ạ. Em có thể giới thiệu cho anh/chị một số dịch vụ khác phù hợp không ạ?"

          7. Với lời chào:
            "Xin chào anh/chị! Em là trợ lý ảo của dichvuhungngan. Em rất vui được hỗ trợ anh/chị tìm hiểu về các dịch vụ của chúng em ạ."

          Bảng ánh xạ danh mục:
          - Thức ăn -> food
          - Đồ uống -> drinks
          - Giặt ủi -> laundry
          - Dạy học -> teaching
          - Điện tử-Vi Tính -> electronics
          - Vận tải -> transport
          - Làm đẹp -> beauty

          Lưu ý:
          - Luôn giữ giọng điệu lịch sự, nhiệt tình và chuyên nghiệp
          - Sử dụng từ ngữ tôn trọng như "anh/chị"
          - Thêm từ "dạ", "ạ" để thể hiện sự lịch sự
          - Luôn sẵn sàng hỗ trợ thêm
          - Tạo cảm giác gần gũi, thân thiện với người dùng
          """},
            {"role": "user", "content": user_message}
        ]

        response = self.client.chat.completions.create(
            messages=messages,
            tools=self.tools,
            model=self.model_name,
        )

        if response.choices[0].finish_reason == "tool_calls":
            messages.append(response.choices[0].message)

            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.type == "function":
                    function_args = json.loads(tool_call.function.arguments.replace("'", '"'))
                    print(f"Calling function `{tool_call.function.name}` with arguments {function_args}")
                    callable_func = getattr(self, tool_call.function.name)
                    function_return = callable_func(**function_args)
                    print(f"Function returned = {function_return}")

                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": function_return,
                        }
                    )

            response = self.client.chat.completions.create(
                messages=messages,
                tools=self.tools,
                model=self.model_name,
            )

        return response

