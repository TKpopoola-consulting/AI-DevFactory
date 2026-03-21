// lib/models/job_model.dart
import 'package:json_annotation/json_annotation.dart';

part 'job_model.g.dart';

@JsonSerializable()
class Job {
  final String id;
  final String prompt;
  final String status;
  final int progress;
  final String? currentStage;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final DateTime? completedAt;
  final JobArtifacts? artifacts;
  final JobCost? cost;
  final JobQuality? quality;
  final List<JobLog>? logs;
  final List<Checkpoint>? checkpoints;
  final Map<String, AgentStatus>? agents;
  
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
  
  factory Job.fromJson(Map<String, dynamic> json) => _$JobFromJson(json);
  Map<String, dynamic> toJson() => _$JobToJson(this);
  
  bool get isRunning => status == 'processing' || status == 'running';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get needsIntervention => status == 'needs_intervention';
}

@JsonSerializable()
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
  
  factory JobArtifacts.fromJson(Map<String, dynamic> json) => _$JobArtifactsFromJson(json);
  Map<String, dynamic> toJson() => _$JobArtifactsToJson(this);
}

@JsonSerializable()
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
  
  factory JobCost.fromJson(Map<String, dynamic> json) => _$JobCostFromJson(json);
  Map<String, dynamic> toJson() => _$JobCostToJson(this);
}

@JsonSerializable()
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
  
  factory JobQuality.fromJson(Map<String, dynamic> json) => _$JobQualityFromJson(json);
  Map<String, dynamic> toJson() => _$JobQualityToJson(this);
}

@JsonSerializable()
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
  
  factory Issue.fromJson(Map<String, dynamic> json) => _$IssueFromJson(json);
  Map<String, dynamic> toJson() => _$IssueToJson(this);
  
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

@JsonSerializable()
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
  
  factory JobLog.fromJson(Map<String, dynamic> json) => _$JobLogFromJson(json);
  Map<String, dynamic> toJson() => _$JobLogToJson(this);
  
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

@JsonSerializable()
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
  
  factory Checkpoint.fromJson(Map<String, dynamic> json) => _$CheckpointFromJson(json);
  Map<String, dynamic> toJson() => _$CheckpointToJson(this);
}

@JsonSerializable()
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
  
  factory AgentStatus.fromJson(Map<String, dynamic> json) => _$AgentStatusFromJson(json);
  Map<String, dynamic> toJson() => _$AgentStatusToJson(this);
}
