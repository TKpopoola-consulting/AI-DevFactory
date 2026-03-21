// lib/services/api_service.dart
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/job_model.dart';
import '../utils/constants.dart';

class ApiService {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: AppConstants.baseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
    },
  ));
  
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  
  ApiService() {
    _addInterceptors();
  }
  
  void _addInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _secureStorage.read(key: AppConstants.keyAccessToken);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Token expired, try to refresh
          await _refreshToken();
          return handler.resolve(await _retry(error.requestOptions));
        }
        return handler.next(error);
      },
    ));
  }
  
  Future<Response> _retry(RequestOptions requestOptions) async {
    final token = await _secureStorage.read(key: AppConstants.keyAccessToken);
    requestOptions.headers['Authorization'] = 'Bearer $token';
    return _dio.fetch(requestOptions);
  }
  
  Future<void> _refreshToken() async {
    final refreshToken = await _secureStorage.read(key: AppConstants.keyRefreshToken);
    if (refreshToken == null) throw Exception('No refresh token');
    
    try {
      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });
      
      final newToken = response.data['access_token'];
      await _secureStorage.write(key: AppConstants.keyAccessToken, value: newToken);
    } catch (e) {
      throw Exception('Failed to refresh token');
    }
  }
  
  // Create a new job
  Future<String> createJob({
    required String prompt,
    required Map<String, dynamic> config,
    required Map<String, dynamic> outputConfig,
  }) async {
    try {
      final response = await _dio.post(AppConstants.apiJobs, data: {
        'prompt': prompt,
        'config': config,
        'output_config': outputConfig,
      });
      
      return response.data['job_id'];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Get job status
  Future<Job> getJobStatus(String jobId) async {
    try {
      final response = await _dio.get(
        AppConstants.apiJobStatus.replaceFirst('{id}', jobId),
      );
      return Job.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Get all jobs
  Future<List<Job>> getJobs() async {
    try {
      final response = await _dio.get('/jobs');
      final List<dynamic> data = response.data;
      return data.map((json) => Job.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Cancel job
  Future<void> cancelJob(String jobId) async {
    try {
      await _dio.post('/jobs/$jobId/cancel');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Retry job
  Future<void> retryJob(String jobId) async {
    try {
      await _dio.post('/jobs/$jobId/retry');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Provide human feedback
  Future<void> provideFeedback(String jobId, String feedback) async {
    try {
      await _dio.post('/jobs/$jobId/feedback', data: {
        'feedback': feedback,
      });
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Rollback to checkpoint
  Future<void> rollbackToCheckpoint(String jobId, String checkpointId) async {
    try {
      await _dio.post('/jobs/$jobId/rollback', data: {
        'checkpoint_id': checkpointId,
      });
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Download project as ZIP
  Future<Response> downloadProject(String jobId) async {
    try {
      return await _dio.get(
        '/jobs/$jobId/download',
        options: Options(responseType: ResponseType.bytes),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  String _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response!.data;
      if (data is Map && data.containsKey('error')) {
        return data['error'];
      }
      return 'Server error: ${error.response!.statusCode}';
    } else if (error.type == DioExceptionType.connectionTimeout) {
      return 'Connection timeout. Please check your network.';
    } else if (error.type == DioExceptionType.receiveTimeout) {
      return 'Server response timeout.';
    } else {
      return 'Network error: ${error.message}';
    }
  }
}
