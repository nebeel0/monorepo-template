import 'package:dio/browser.dart';
import 'package:dio/dio.dart';

/// Web-specific client setup — uses cookies for authentication.
void setupClient(Dio dio) {
  final adapter = BrowserHttpClientAdapter();
  adapter.withCredentials = true; // Enable cookie-based auth
  dio.httpClientAdapter = adapter;
}
