class Environment {
  static const String environment =
      String.fromEnvironment('ENVIRONMENT', defaultValue: 'dev');

  static String get baseUrl {
    switch (environment) {
      case 'prod':
        return 'https://api.example.com';
      case 'staging':
        return 'https://staging-api.example.com';
      default:
        return 'http://localhost:8000';
    }
  }
}
