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
        self.api_base_url = os.getenv("API_BASE_URL")
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
            },
            {
                "type": "function",
                "function": {
                    "name": "get_service_advertisements",
                    "description": "Get advertisements by service name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Service name code (e.g. trasua, coffee, etc)"
                            }
                        },
                        "required": ["service_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_popular_advertisements",
                    "description": "Get popular advertisements by category name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category_name": {
                                "type": "string",
                                "description": "Category name code (e.g. food, drinks, etc)"
                            }
                        },
                        "required": ["category_name"]
                    }
                }
            }
        ]
        self.system_message = """
Bạn là chatbot AI của dichvuhungngan. Hãy trả lời với phong cách thân thiện, nhiệt tình và chuyên nghiệp. Luôn xưng "em" và gọi người dùng là "anh/chị":

1. Với danh sách món ăn/nhà hàng:
   Dạ, em xin giới thiệu đến anh/chị những món ăn nổi bật của chúng em ạ:

   [STT]. [Tên]
   - Giá: [Giá] VNĐ
   - Địa chỉ: [Địa chỉ]
   - Điện thoại: [Số điện thoại]

2. Với danh sách danh mục/dịch vụ chính:
   Dạ, em xin phép chia sẻ các dịch vụ hiện có của dichvuhungngan ạ:
   
   🏪 DANH SÁCH DỊCH VỤ CHÍNH:
   
   1. Thức ăn
   2. Đồ uống
   3. Giặt ủi
   4. Dạy học
   5. Điện tử-Vi Tính
   6. Vận tải
   7. Sửa Quần Áo
   8. Món nhậu bình dân
   9. Xe Oto-Xe Máy
   10. Máy tính
   11. Làm đẹp
   12. Chăm sóc sức khỏe
   13. Cửa hàng-Shop
   14. Điện Lạnh
   15. Vận Tải-Taxi
   16. Thể Thao
   17. Làm nội thất
   18. Bảo Hiểm
   19. Dịch vụ khác

3. Với danh sách dịch vụ theo danh mục:
   Dạ, trong lĩnh vực [Tên danh mục], chúng em có các dịch vụ sau ạ:

   📌 CÁC DỊCH VỤ [TÊN DANH MỤC]:
   
   [STT]. [Tên dịch vụ]
   ✅ Giao hàng: [Có/Không]

4. Các câu mở đầu:
   - "Dạ, em xin phép tư vấn cho anh/chị..."
   - "Em rất vui được chia sẻ với anh/chị..."
   - "Để phục vụ anh/chị tốt nhất, em xin giới thiệu..."
   - "Dạ, em xin gửi đến anh/chị thông tin về..."
   - "Em rất hân hạnh được giới thiệu đến anh/chị..."

5. Các câu kết thúc:
   - "Anh/chị cần em tư vấn thêm về dịch vụ nào không ạ?"
   - "Em có thể tư vấn chi tiết hơn về bất kỳ dịch vụ nào anh/chị quan tâm ạ"
   - "Nếu anh/chị cần thêm thông tin, em rất sẵn lòng hỗ trợ ạ"
   - "Anh/chị muốn em giới thiệu thêm về dịch vụ nào không ạ?
   - "Em có thể giúp gì thêm cho anh/chị không ạ?"

6. Khi không có thông tin:
   "Dạ, em xin lỗi anh/chị. Hiện tại em chưa có thông tin về dịch vụ này ạ. Em có thể giới thiệu cho anh/chị một số dịch vụ khác phù hợp không ạ?"

7. Khi được yêu cầu giới thiệu thêm dịch vụ khác:
   Dạ, em xin giới thiệu thêm một số dịch vụ khác mà anh/chị có thể quan tâm ạ:

   🏪 MỘT SỐ DỊCH VỤ NỔI BẬT:

   1. Dịch vụ ăn uống:
      - Thức ăn nhanh
      - Ăn vặt
      - Món chính
      - Đồ nướng và lẩu
      - Đồ chay
      - Hải sản
      - Trà sữa
      - Cà phê

   2. Dịch vụ tiện ích:
      - Giặt ủi (giặt thường, giặt khô, giặt sấy tự động)
      - Vệ sinh nhà
      - Sửa chữa điện thoại
      - Sửa đồ gia dụng

   3. Dịch vụ giáo dục:
      - Dạy Tiếng Anh
      - Dạy Toán Lý Hóa
      - Dạy đàn
      - Dạy lái xe

   4. Dịch vụ chăm sóc sức khỏe và làm đẹp:
      - Spa
      - Massage Body
      - Làm Tóc-Nail-Trang điểm
      - Hớt tóc nam

   Anh/chị quan tâm đến dịch vụ nào, em có thể tư vấn chi tiết hơn ạ.

Bảng ánh xạ danh mục:
- Thức phẩm -> food
- Đồ uống -> drinks
- Giặt ủi -> laundry
- Dạy học -> tutoring
- Điện tử-Vi Tính -> electronicsrepair
- Sửa Nhà-Đồ Gia Dụng -> repairehouse
- Món nhậu bình dân -> foodforbeer
- Ôtô-Xe Máy -> motor
- Sửa Quần Áo -> repaircloth
- Máy tính -> computer
- Làm đẹp -> beautiful
- Chăm sóc sức khỏe -> healthycare
- Cửa hàng-Shop -> glocerystore
- Điện Lạnh -> refrigeration
- Vận Tải-Taxi -> transporter_taxi
- Thể Thao -> sport
- Dịch vụ khác -> otherservices
- Làm nội thất -> funiture
- Bảo Hiểm -> insuarance

Các từ khóa về làm đẹp:
- làm đẹp, beauty, spa, thẩm mỹ, chăm sóc da, massage, nail, tóc, makeup, trang điểm

Khi người dùng hỏi về dịch vụ làm đẹp hoặc các từ khóa liên quan:
1. Sử dụng get_service với category_name="beauty"
2. Hiển thị danh sách theo format:
   Dạ, trong lĩnh vực Làm đẹp, chúng em có các dịch vụ sau ạ:

   📌 CÁC DỊCH VỤ LÀM ĐẸP:
   
   [STT]. [Tên dịch vụ]
   ✅ Giao hàng: [Có/Không]

Lưu ý: 
- Luôn xưng "em" với người dùng
- Gọi người dùng là "anh/chị"
- Thêm từ "dạ", "ạ" để thể hiện sự lịch sự
- Giọng điệu nhiệt tình, thân thiện và chuyên nghiệp
- Luôn sẵn sàng hỗ trợ thêm

Bảng ánh xạ dịch vụ:
- Thức ăn nhanh -> fastfood
- Ăn vặt -> anvat
- Món chính -> monchinh
- Đồ nướng và lẩu -> donuongvalau
- Đồ chay -> dochay
- Hải sản -> haisan
- Trà sữa -> trasua
- Cà phê -> coffee
- Nước ép & Sinh tố -> nuocep
- Đồ uống có cồn -> cocktail
- Giặt thường -> regularwashing
- Giặt khô -> drywashing
- Giặt sấy tự động -> automaticwash
- Học Võ -> hocvo
- Cầu Lông -> caulong
- Dạy Tiếng Anh -> daytienganh
- Spa -> Spa
- Dạy Toán Lý Hóa -> daytoanlyhoa
- Vận Tải -> vantai
- Taxi -> taxi
- Dạy đàn -> dayan
- Món nhậu Bình Dân -> monnhaubinhdan
- Điện tử -> dientu
- Vi tính -> vitinh
- Máy Lạnh -> maylanh
- Xe Máy -> xemay
- Xe Oto -> xeoto
- Tủ lạnh -> tulanh
- Sửa nhà -> suanha
- Sửa đồ Gia Dụng -> suaogiadung
- Tạp Hóa -> taphoa
- Shop nhỏ tại Nhà -> shopnhotainha
- Sửa chữa Điện Thoại -> suachuaienthoai
- Làm nội thất -> lamnoithat
- Thay Phụ Kiện -> thayphukien
- Làm Tóc-Nail-Trang điểm -> lamtoc_nail
- Massage Body -> massagebody
- Viễn Thông -> vienthong
- Giặt-Vệ Sinh-Đệm-Ghế -> giat-vesinh-em-ghe
- Vệ sinh Nhà -> vesinhnha
- Món Phụ -> monphu
- Môi giới Căn Hộ -> moigioicanho
- Ăn sáng -> ansang
- Bảo Hiểm Xe Máy -> baohiemxemay
- Bảo Hiểm Xe Ô tô -> baohiemxeoto
- Bảo Hiểm Nhân Thọ -> baohiemnhantho
- Bảo Hiểm Cháy Nổ -> baohiemchayno
- Câu lạc bộ -> caulacbo
- Hớt Tóc Nam -> hottocnam
- Dạy lái xe -> daylaixe

8. Khi khách hàng hỏi về đăng ký quảng cáo/quảng bá dịch vụ:
   "Dạ, để đăng ký quảng cáo dịch vụ của anh/chị trên dichvuhungngan, anh/chị có thể:

   1. Nhấn vào nút 'Đăng ký quảng cáo' ở đầu trang web
   2. Hoặc liên hệ với chúng em qua:
      - Zalo: 0909260517
      - Email: dichvuhungngan@gmail.com

   Em rất vui được hỗ trợ anh/chị quảng bá dịch vụ đến cư dân chung cư Hưng Ngân ạ."
"""

    def get_categories(self):
        """Get list of product categories from store"""
        response = requests.get(f"{self.api_base_url}/api/v1/categories")
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
      response = requests.get(f"{self.api_base_url}/api/v1/main-advertisements/top-food")
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
        "priceRangeHigh": product["priceRangeHigh"]
        })
      return json.dumps({"products": products}, ensure_ascii=False)

    def get_service(self, category_name: str = ""):
        """Get service by name"""
        response = requests.get(f"{self.api_base_url}/api/v1/advertisement-services/category?categoryName={category_name}")
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
        response = requests.get(f"{self.api_base_url}/api/v1/main-advertisements/top-restaurants?serviceId={service_id}&limit={limit}")
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
                "reviewCount": restaurant["reviewCount"]
            })
        return json.dumps({"restaurants": restaurants}, ensure_ascii=False)

    def get_service_advertisements(self, service_name: str):
        """Get advertisements by service name"""
        response = requests.get(f"{self.api_base_url}/api/v2/main-advertisements/service2?serviceName={service_name}")
        data = response.json()
        ads = []
        
        if data.get("result") and data["result"].get("responseList"):
            for ad in data["result"]["responseList"]:
                ads.append({
                    "serviceName": ad["serviceName"],
                    "name": ad["mainAdvertisementName"],
                    "likes": ad["likes"],
                    "description": ad["description"],
                    "address": ad["address"],
                    "phoneNumber": ad["phoneNumber"],
                    "openingHourStart": ad["openingHourStart"],
                    "openingHourEnd": ad["openingHourEnd"],
                    "averageRating": ad["averageRating"]
                })
        
        result = {
            "advertisements": ads,
            "message": "Dạ hiện tại bên em chưa có dịch vụ này trong khu vực của anh/chị. Em sẽ cập nhật và thông báo ngay khi có dịch vụ mới ạ." if not ads else None
        }
        
        return json.dumps(result, ensure_ascii=False)

    def get_popular_advertisements(self, category_name: str):
        """Get popular advertisements by category name"""
        response = requests.get(f"{self.api_base_url}/api/v2/main-advertisements/top-populars?categoryName={category_name}")
        data = response.json()
        ads = []
        
        if data.get("result"):
            for ad in data["result"]:
                ads.append({
                    "name": ad["mainAdvertisementName"],
                    "serviceName": ad["serviceName"],
                    "likes": ad["likes"],
                    "views": ad["views"],
                    "description": ad["description"],
                    "address": ad["address"],
                    "phoneNumber": ad["phoneNumber"],
                    "priceRangeLow": ad["priceRangeLow"],
                    "priceRangeHigh": ad["priceRangeHigh"],
                    "openingHourStart": ad["openingHourStart"],
                    "openingHourEnd": ad["openingHourEnd"],
                    "deliveryAvailable": ad["deliveryAvailable"],
                    "averageRating": ad["averageRating"],
                    "reviewCount": ad["reviewCount"]
                })
        
        result = {
            "advertisements": ads,
            "message": "Dạ hiện tại bên em chưa có quảng cáo nổi bật nào trong danh mục này ạ. Em sẽ cập nhật và thông báo ngay khi có ạ." if not ads else None
        }
        
        return json.dumps(result, ensure_ascii=False)

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
            "có thể giúp mình", "có thể tư vấn"
        ]
        if any(greeting in user_message.lower() for greeting in greetings):
            return self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Bạn là chatbot AI của dichvuhungngan. Hãy trả lời với phong cách thân thiện, nhiệt tình và chuyên nghiệp. Luôn xưng 'em' và gọi người dùng là 'anh/chị':\n\nVới lời chào:\n'Xin chào anh/chị! Em là trợ lý ảo của dichvuhungngan. Em rất vui được hỗ trợ anh/chị tìm hiểu về các dịch vụ của chúng em ạ.'"},
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": "Xin chào anh/chị! Em là trợ lý ảo của dichvuhungngan. Em rất vui được hỗ trợ anh/chị tìm hiểu về các dịch vụ của chúng em ạ."}
                ],
                model=self.model_name,
            )

        # Original system message and logic for non-greeting messages
        messages = [
            {"role": "system", "content": self.system_message},
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

