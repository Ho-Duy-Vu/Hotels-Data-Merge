Tên bài: Parse and merge hotel data from different suppliers
Background (Bối cảnh)
Trong bất kỳ trang web đặt phòng khách sạn nào như Kaligo.com do Ascenda vận hành, có rất nhiều nỗ lực được thực hiện để hiển thị nội dung một cách sạch sẽ và có tổ chức. Tuy nhiên, đằng sau đó, quy trình thu thập dữ liệu rất phức tạp và dữ liệu thường xuyên bị sai lệch hoặc "bẩn" (dirty).
Bài tập này cung cấp cho bạn một cái nhìn tổng quan về một số thao tác chúng tôi thực hiện để làm sạch dữ liệu trước khi đưa lên trang web:

Truy vấn nhiều nhà cung cấp (suppliers) để đồng hóa dữ liệu từ các nguồn khác nhau.

Xây dựng tập dữ liệu hoàn chỉnh nhất có thể.

Làm sạch (sanitize) chúng để loại bỏ dữ liệu bẩn.

v.v.

Your Task (Nhiệm vụ của bạn)
Viết một phiên bản đơn giản hóa của quy trình thu thập và gộp dữ liệu:

Fetch (Tải) dữ liệu khách sạn thô từ các nhà cung cấp khác nhau.

Parse (Phân tích cú pháp) và làm sạch dữ liệu thô.

Mỗi nhà cung cấp có thể trả về các thuộc tính khác nhau về cùng một khách sạn. Hãy Merge (gộp) chúng lại và giữ lại những gì bạn cho là dữ liệu tốt nhất.

Trả về dữ liệu đã được gộp dưới định dạng JSON.

Requirements (Yêu cầu hệ thống)

Viết một hàm hỗ trợ các đầu vào (inputs) sau để lọc: destination_ids, hotel_ids. Khi được gọi, hàm phải trả về một mảng dữ liệu khách sạn định dạng JSON.

Các khách sạn được trả về phải khớp với tất cả các hotel_ids và destination_ids được cung cấp ở đầu vào. Nếu một khách sạn khớp destination_ids nhưng không khớp hotel_ids, nó không được trả về.

Nếu không có hotel_id và destination_id nào được truyền vào, trả về tất cả các khách sạn.

Mỗi khách sạn chỉ được trả về 1 lần duy nhất (vì bạn đã gộp dữ liệu thành các bản ghi độc nhất).

JSON Structure (Cấu trúc dữ liệu JSON mong đợi)
Đề bài cung cấp một mẫu cấu trúc JSON rất chi tiết bao gồm các trường:

id, destination_id, name

location: lat, lng, address, city, country

description

amenities: general (list), room (list)

images: rooms (list of objects with link & description), site (list), amenities (list)

booking_conditions (list of strings).

Supplier Data (Dữ liệu Nhà cung cấp)
Có 3 nhà cung cấp với các URL mock API:

Acme: https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme

Patagonia: https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/patagonia

Paperflies: https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/paperflies

Giả định (Assumptions):

ID của khách sạn và điểm đến đã được làm sạch sẵn. Bạn có thể dựa vào các ID này để gộp dữ liệu.

Link hình ảnh đã được xác minh là hoạt động tốt, bạn chỉ cần quan tâm đến việc tổ chức chúng.

Dữ liệu từ nhà cung cấp có thể thay đổi theo thời gian, vì vậy giải pháp của bạn phải linh hoạt để luôn trả về dữ liệu có chất lượng tốt nhất.

What we're expecting (Tiêu chí đánh giá của Ascenda)

Đây KHÔNG PHẢI là một bài toán đánh đố thuật toán kiểu "Leetcode". Chúng tôi quan tâm đến cách giải pháp của bạn giải quyết vấn đề một cách thanh lịch (elegantly).

Đánh giá cao Code Cleanliness (Code sạch). Hãy sử dụng Design Patterns (Mẫu thiết kế) và các phương pháp tổ chức mã nguồn tốt.

Hệ thống lý tưởng phải cho thấy cách bạn xử lý việc gộp dữ liệu nếu trong tương lai có thêm rất nhiều nhà cung cấp khác.

Không cần sử dụng các phương pháp phân tích dữ liệu (Data-analytics) hay Machine Learning phức tạp. Các quy tắc so khớp đơn giản viết bằng code (simple rules in code) là đủ.