import 'package:flutter/material.dart';

class Job {
  String id;
  String prompt;
  String status;
  int progress;
  String? currentStage;
  DateTime createdAt;
  DateTime? updatedAt;
  DateTime? completedAt;
  JobArtifacts? artifacts;
  JobCost? cost;
  JobQuality? quality;
  List<JobLog>? logs;
  List<Checkpoint>? checkpoints;
  Map<String, AgentStatus>? agents;

  Job({
    required this.id,
    required this.prompt,
    required this.status,
    required this.progress,
    this.currentStage,
    required this.createdAt,
    this.updatedAt,
    this.completedAt,
    this.artifacts,
    this.cost,
    this.quality,
    this.logs,
    this.checkpoints,
    this.agents,
  });

  factory Job.fromJson(Map<String, dynamic> json) {
    return Job(
      id: json['job_id'] ?? json['id'] ?? '',
      prompt: json['prompt'] ?? '',
      status: json['status'] ?? 'created',
      progress: json['progress'] ?? 0,
      currentStage: json['current_stage'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : DateTime.now(),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
      completedAt: json['completed_at'] != null 
          ? DateTime.parse(json['completed_at']) 
          : null,
      artifacts: json['artifacts'] != null 
          ? JobArtifacts.fromJson(json['artifacts']) 
          : null,
      cost: json['cost'] != null 
          ? JobCost.fromJson(json['cost']) 
          : null,
      quality: json['quality'] != null 
          ? JobQuality.fromJson(json['quality']) 
          : null,
      logs: json['logs'] != null 
          ? (json['logs'] as List).map((l) => JobLog.fromJson(l)).toList()
          : null,
      checkpoints: json['checkpoints'] != null 
          ? (json['checkpoints'] as List).map((c) => Checkpoint.fromJson(c)).toList()
          : null,
      agents: json['agents'] != null 
          ? (json['agents'] as Map).map((k, v) => MapEntry(k, AgentStatus.fromJson(v)))
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'job_id': id,
      'prompt': prompt,
      'status': status,
      'progress': progress,
      'current_stage': currentStage,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'artifacts': artifacts?.toJson(),
      'cost': cost?.toJson(),
      'quality': quality?.toJson(),
      'logs': logs?.map((l) => l.toJson()).toList(),
      'checkpoints': checkpoints?.map((c) => c.toJson()).toList(),
      'agents': agents?.map((k, v) => MapEntry(k, v.toJson())),
    };
  }

  bool get isRunning => status == 'processing' || status == 'running';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get needsIntervention => status == 'needs_intervention';
}

class JobArtifacts {
  final String? githubPrUrl;
  final String? downloadUrl;
  final String? blobUrl;
  final int fileCount;
  final int linesOfCode;
  final Map<String, String>? files;

  JobArtifacts({
    this.githubPrUrl,
    this.downloadUrl,
    this.blobUrl,
    required this.fileCount,
    required this.linesOfCode,
    this.files,
  });

  factory JobArtifacts.fromJson(Map<String, dynamic> json) {
    return JobArtifacts(
      githubPrUrl: json['github_pr_url'],
      downloadUrl: json['download_url'],
      blobUrl: json['blob_url'],
      fileCount: json['file_count'] ?? 0,
      linesOfCode: json['lines_of_code'] ?? 0,
      files: json['files'] != null 
          ? Map<String, String>.from(json['files']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'github_pr_url': githubPrUrl,
      'download_url': downloadUrl,
      'blob_url': blobUrl,
      'file_count': fileCount,
      'lines_of_code': linesOfCode,
      'files': files,
    };
  }
}

class JobCost {
  final double total;
  final int aiTokens;
  final double aiCost;
  final int computeSeconds;
  final double computeCost;
  final int storageMb;
  final double storageCost;
  final String currency;

  JobCost({
    required this.total,
    required this.aiTokens,
    required this.aiCost,
    required this.computeSeconds,
    required this.computeCost,
    required this.storageMb,
    required this.storageCost,
    required this.currency,
  });

  factory JobCost.fromJson(Map<String, dynamic> json) {
    return JobCost(
      total: (json['total'] ?? 0).toDouble(),
      aiTokens: json['ai_tokens'] ?? 0,
      aiCost: (json['ai_cost'] ?? 0).toDouble(),
      computeSeconds: json['compute_seconds'] ?? 0,
      computeCost: (json['compute_cost'] ?? 0).toDouble(),
      storageMb: json['storage_mb'] ?? 0,
      storageCost: (json['storage_cost'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'USD',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total': total,
      'ai_tokens': aiTokens,
      'ai_cost': aiCost,
      'compute_seconds': computeSeconds,
      'compute_cost': computeCost,
      'storage_mb': storageMb,
      'storage_cost': storageCost,
      'currency': currency,
    };
  }
}

class JobQuality {
  final double overall;
  final double security;
  final double tests;
  final double coverage;
  final double performance;
  final List<Issue> issues;
  final List<String> recommendations;

  JobQuality({
    required this.overall,
    required this.security,
    required this.tests,
    required this.coverage,
    required this.performance,
    required this.issues,
    required this.recommendations,
  });

  factory JobQuality.fromJson(Map<String, dynamic> json) {
    return JobQuality(
      overall: (json['overall'] ?? 0).toDouble(),
      security: (json['security'] ?? 0).toDouble(),
      tests: (json['tests'] ?? 0).toDouble(),
      coverage: (json['coverage'] ?? 0).toDouble(),
      performance: (json['performance'] ?? 0).toDouble(),
      issues: json['issues'] != null 
          ? (json['issues'] as List).map((i) => Issue.fromJson(i)).toList()
          : [],
      recommendations: json['recommendations'] != null 
          ? List<String>.from(json['recommendations'])
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'overall': overall,
      'security': security,
      'tests': tests,
      'coverage': coverage,
      'performance': performance,
      'issues': issues.map((i) => i.toJson()).toList(),
      'recommendations': recommendations,
    };
  }
}

class Issue {
  final String id;
  final String title;
  final String severity;
  final String? file;
  final int? line;
  final String description;
  final String? suggestedFix;

  Issue({
    required this.id,
    required this.title,
    required this.severity,
    this.file,
    this.line,
    required this.description,
    this.suggestedFix,
  });

  factory Issue.fromJson(Map<String, dynamic> json) {
    return Issue(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      severity: json['severity'] ?? 'medium',
      file: json['file'],
      line: json['line'],
      description: json['description'] ?? '',
      suggestedFix: json['suggested_fix'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'severity': severity,
      'file': file,
      'line': line,
      'description': description,
      'suggested_fix': suggestedFix,
    };
  }

  Color get severityColor {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Colors.red;
      case 'high':
        return Colors.orange;
      case 'medium':
        return Colors.yellow;
      default:
        return Colors.blue;
    }
  }
}

class JobLog {
  final DateTime timestamp;
  final String level;
  final String message;
  final String? agent;

  JobLog({
    required this.timestamp,
    required this.level,
    required this.message,
    this.agent,
  });

  factory JobLog.fromJson(Map<String, dynamic> json) {
    return JobLog(
      timestamp: json['timestamp'] != null 
          ? DateTime.parse(json['timestamp']) 
          : DateTime.now(),
      level: json['level'] ?? 'info',
      message: json['message'] ?? '',
      agent: json['agent'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'level': level,
      'message': message,
      'agent': agent,
    };
  }

  Color get levelColor {
    switch (level.toLowerCase()) {
      case 'error':
        return Colors.red;
      case 'warning':
        return Colors.orange;
      case 'info':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }
}

class Checkpoint {
  final String id;
  final String stage;
  final DateTime timestamp;
  final bool isRestorable;

  Checkpoint({
    required this.id,
    required this.stage,
    required this.timestamp,
    required this.isRestorable,
  });

  factory Checkpoint.fromJson(Map<String, dynamic> json) {
    return Checkpoint(
      id: json['id'] ?? '',
      stage: json['stage'] ?? '',
      timestamp: json['timestamp'] != null 
          ? DateTime.parse(json['timestamp']) 
          : DateTime.now(),
      isRestorable: json['is_restorable'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'stage': stage,
      'timestamp': timestamp.toIso8601String(),
      'is_restorable': isRestorable,
    };
  }
}

class AgentStatus {
  final String name;
  final String status;
  final int progress;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final String? error;

  AgentStatus({
    required this.name,
    required this.status,
    required this.progress,
    this.startedAt,
    this.completedAt,
    this.error,
  });

  factory AgentStatus.fromJson(Map<String, dynamic> json) {
    return AgentStatus(
      name: json['name'] ?? '',
      status: json['status'] ?? 'pending',
      progress: json['progress'] ?? 0,
      startedAt: json['started_at'] != null 
          ? DateTime.parse(json['started_at']) 
          : null,
      completedAt: json['completed_at'] != null 
          ? DateTime.parse(json['completed_at']) 
          : null,
      error: json['error'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'status': status,
      'progress': progress,
      'started_at': startedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'error': error,
    };
  }
}
