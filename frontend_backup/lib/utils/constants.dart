// lib/utils/constants.dart
class AppConstants {
  static const String appName = 'AI DevFactory';
  static const String appVersion = '2.0.0';
  
  // API Endpoints
  static const String baseUrl = 'http://localhost:8000';
  static const String wsUrl = 'ws://localhost:8000';
  
  static const String apiJobs = '/jobs';
  static const String apiJobStatus = '/jobs/{id}';
  static const String apiExport = '/jobs/{id}/export';
  static const String wsJob = '/ws/{id}';
  
  // Storage Keys
  static const String keyThemeMode = 'theme_mode';
  static const String keyAccessToken = 'access_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserId = 'user_id';
  static const String keySettings = 'app_settings';
  
  // Agent Types
  static const List<String> frontendFrameworks = [
    'React', 'Flutter', 'Vue.js', 'Angular', 'Svelte'
  ];
  
  static const List<String> backendFrameworks = [
    'FastAPI', 'Django', 'Express.js', 'NestJS', 'Spring Boot'
  ];
  
  static const List<String> cloudProviders = [
    'Azure', 'AWS', 'GCP'
  ];
  
  static const List<String> databases = [
    'PostgreSQL', 'MongoDB', 'MySQL', 'Cosmos DB', 'DynamoDB'
  ];
  
  // Pricing (per 1000 tokens)
  static const double aiTokenPrice = 0.01;
  static const double computePricePerHour = 0.06;
  static const double storagePricePerGB = 0.021;
  
  // Quality thresholds
  static const double qualityTarget = 90.0;
  static const double qualityMinimum = 70.0;
  static const int maxIterations = 5;
}
