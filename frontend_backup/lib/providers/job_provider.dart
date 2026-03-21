// lib/providers/job_provider.dart
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import '../models/job_model.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class JobProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  List<Job> _jobs = [];
  Job? _currentJob;
  bool _isLoading = false;
  String? _error;
  WebSocketChannel? _channel;
  
  List<Job> get jobs => _jobs;
  Job? get currentJob => _currentJob;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  // Create new job
  Future<String> createJob({
    required String prompt,
    required Map<String, dynamic> config,
    required Map<String, dynamic> outputConfig,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final jobId = await _apiService.createJob(
        prompt: prompt,
        config: config,
        outputConfig: outputConfig,
      );
      
      // Connect to WebSocket for real-time updates
      _connectWebSocket(jobId);
      
      _isLoading = false;
      notifyListeners();
      return jobId;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      rethrow;
    }
  }
  
  // Get job status
  Future<void> getJobStatus(String jobId) async {
    try {
      final job = await _apiService.getJobStatus(jobId);
      _updateJob(job);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  // Get all jobs
  Future<void> getJobs() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      _jobs = await _apiService.getJobs();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Cancel job
  Future<void> cancelJob(String jobId) async {
    try {
      await _apiService.cancelJob(jobId);
      if (_currentJob?.id == jobId) {
        _currentJob?.status = 'cancelled';
        notifyListeners();
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  // Retry job
  Future<void> retryJob(String jobId) async {
    try {
      await _apiService.retryJob(jobId);
      if (_currentJob?.id == jobId) {
        _connectWebSocket(jobId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  // Provide human feedback
  Future<void> provideFeedback(String jobId, String feedback) async {
    try {
      await _apiService.provideFeedback(jobId, feedback);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  // Rollback to checkpoint
  Future<void> rollbackToCheckpoint(String jobId, String checkpointId) async {
    try {
      await _apiService.rollbackToCheckpoint(jobId, checkpointId);
      if (_currentJob?.id == jobId) {
        _connectWebSocket(jobId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  // WebSocket connection for real-time updates
  void _connectWebSocket(String jobId) {
    _channel = WebSocketChannel.connect(
      Uri.parse('${AppConstants.wsUrl}${AppConstants.wsJob.replaceFirst('{id}', jobId)}'),
    );
    
    _channel!.stream.listen(
      (message) {
        final data = jsonDecode(message);
        _handleWebSocketMessage(data);
      },
      onError: (error) {
        print('WebSocket error: $error');
      },
      onDone: () {
        print('WebSocket connection closed');
      },
    );
  }
  
  void _handleWebSocketMessage(Map<String, dynamic> data) {
    final type = data['type'] as String?;
    
    switch (type) {
      case 'progress':
        _updateProgress(data['data']);
        break;
      case 'log':
        _addLog(data['data']);
        break;
      case 'agent_status':
        _updateAgentStatus(data['data']);
        break;
      case 'checkpoint':
        _addCheckpoint(data['data']);
        break;
      case 'quality_update':
        _updateQuality(data['data']);
        break;
      case 'human_intervention':
        _handleHumanIntervention(data['data']);
        break;
      case 'completed':
        _handleCompletion(data['data']);
        break;
    }
  }
  
  void _updateProgress(Map<String, dynamic> data) {
    if (_currentJob != null) {
      _currentJob!.progress = data['progress'] ?? _currentJob!.progress;
      _currentJob!.currentStage = data['stage'];
      _currentJob!.status = data['status'];
      notifyListeners();
    }
  }
  
  void _addLog(Map<String, dynamic> data) {
    if (_currentJob != null) {
      final log = JobLog.fromJson(data);
      _currentJob!.logs ??= [];
      _currentJob!.logs!.add(log);
      notifyListeners();
    }
  }
  
  void _updateAgentStatus(Map<String, dynamic> data) {
    if (_currentJob != null) {
      _currentJob!.agents ??= {};
      _currentJob!.agents![data['name']] = AgentStatus.fromJson(data);
      notifyListeners();
    }
  }
  
  void _addCheckpoint(Map<String, dynamic> data) {
    if (_currentJob != null) {
      final checkpoint = Checkpoint.fromJson(data);
      _currentJob!.checkpoints ??= [];
      _currentJob!.checkpoints!.add(checkpoint);
      notifyListeners();
    }
  }
  
  void _updateQuality(Map<String, dynamic> data) {
    if (_currentJob != null) {
      _currentJob!.quality = JobQuality.fromJson(data);
      notifyListeners();
    }
  }
  
  void _handleHumanIntervention(Map<String, dynamic> data) {
    if (_currentJob != null) {
      _currentJob!.status = 'needs_intervention';
      _currentJob!.currentStage = 'human_intervention_required';
      notifyListeners();
    }
  }
  
  void _handleCompletion(Map<String, dynamic> data) {
    if (_currentJob != null) {
      _currentJob!.status = 'completed';
      _currentJob!.completedAt = DateTime.parse(data['timestamp']);
      _currentJob!.artifacts = JobArtifacts.fromJson(data['artifacts']);
      _channel?.sink.close();
      notifyListeners();
    }
  }
  
  void _updateJob(Job job) {
    if (_currentJob?.id == job.id) {
      _currentJob = job;
    } else {
      final index = _jobs.indexWhere((j) => j.id == job.id);
      if (index != -1) {
        _jobs[index] = job;
      } else {
        _jobs.add(job);
      }
    }
    notifyListeners();
  }
  
  void setCurrentJob(Job job) {
    _currentJob = job;
    notifyListeners();
  }
  
  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }
}
