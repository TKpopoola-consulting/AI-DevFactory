// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'job_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Job _$JobFromJson(Map<String, dynamic> json) => Job(
      id: json['id'] as String,
      prompt: json['prompt'] as String,
      status: json['status'] as String,
      progress: (json['progress'] as num).toInt(),
      currentStage: json['currentStage'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      artifacts: json['artifacts'] == null
          ? null
          : JobArtifacts.fromJson(json['artifacts'] as Map<String, dynamic>),
      cost: json['cost'] == null
          ? null
          : JobCost.fromJson(json['cost'] as Map<String, dynamic>),
      quality: json['quality'] == null
          ? null
          : JobQuality.fromJson(json['quality'] as Map<String, dynamic>),
      logs: (json['logs'] as List<dynamic>?)
          ?.map((e) => JobLog.fromJson(e as Map<String, dynamic>))
          .toList(),
      checkpoints: (json['checkpoints'] as List<dynamic>?)
          ?.map((e) => Checkpoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      agents: (json['agents'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, AgentStatus.fromJson(e as Map<String, dynamic>)),
      ),
    );

Map<String, dynamic> _$JobToJson(Job instance) => <String, dynamic>{
      'id': instance.id,
      'prompt': instance.prompt,
      'status': instance.status,
      'progress': instance.progress,
      'currentStage': instance.currentStage,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt?.toIso8601String(),
      'completedAt': instance.completedAt?.toIso8601String(),
      'artifacts': instance.artifacts,
      'cost': instance.cost,
      'quality': instance.quality,
      'logs': instance.logs,
      'checkpoints': instance.checkpoints,
      'agents': instance.agents,
    };

JobArtifacts _$JobArtifactsFromJson(Map<String, dynamic> json) => JobArtifacts(
      githubPrUrl: json['githubPrUrl'] as String?,
      downloadUrl: json['downloadUrl'] as String?,
      blobUrl: json['blobUrl'] as String?,
      fileCount: (json['fileCount'] as num).toInt(),
      linesOfCode: (json['linesOfCode'] as num).toInt(),
      files: (json['files'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ),
    );

Map<String, dynamic> _$JobArtifactsToJson(JobArtifacts instance) =>
    <String, dynamic>{
      'githubPrUrl': instance.githubPrUrl,
      'downloadUrl': instance.downloadUrl,
      'blobUrl': instance.blobUrl,
      'fileCount': instance.fileCount,
      'linesOfCode': instance.linesOfCode,
      'files': instance.files,
    };

JobCost _$JobCostFromJson(Map<String, dynamic> json) => JobCost(
      total: (json['total'] as num).toDouble(),
      aiTokens: (json['aiTokens'] as num).toInt(),
      aiCost: (json['aiCost'] as num).toDouble(),
      computeSeconds: (json['computeSeconds'] as num).toInt(),
      computeCost: (json['computeCost'] as num).toDouble(),
      storageMb: (json['storageMb'] as num).toInt(),
      storageCost: (json['storageCost'] as num).toDouble(),
      currency: json['currency'] as String,
    );

Map<String, dynamic> _$JobCostToJson(JobCost instance) => <String, dynamic>{
      'total': instance.total,
      'aiTokens': instance.aiTokens,
      'aiCost': instance.aiCost,
      'computeSeconds': instance.computeSeconds,
      'computeCost': instance.computeCost,
      'storageMb': instance.storageMb,
      'storageCost': instance.storageCost,
      'currency': instance.currency,
    };

JobQuality _$JobQualityFromJson(Map<String, dynamic> json) => JobQuality(
      overall: (json['overall'] as num).toDouble(),
      security: (json['security'] as num).toDouble(),
      tests: (json['tests'] as num).toDouble(),
      coverage: (json['coverage'] as num).toDouble(),
      performance: (json['performance'] as num).toDouble(),
      issues: (json['issues'] as List<dynamic>)
          .map((e) => Issue.fromJson(e as Map<String, dynamic>))
          .toList(),
      recommendations: (json['recommendations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$JobQualityToJson(JobQuality instance) =>
    <String, dynamic>{
      'overall': instance.overall,
      'security': instance.security,
      'tests': instance.tests,
      'coverage': instance.coverage,
      'performance': instance.performance,
      'issues': instance.issues,
      'recommendations': instance.recommendations,
    };

Issue _$IssueFromJson(Map<String, dynamic> json) => Issue(
      id: json['id'] as String,
      title: json['title'] as String,
      severity: json['severity'] as String,
      file: json['file'] as String?,
      line: (json['line'] as num?)?.toInt(),
      description: json['description'] as String,
      suggestedFix: json['suggestedFix'] as String?,
    );

Map<String, dynamic> _$IssueToJson(Issue instance) => <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'severity': instance.severity,
      'file': instance.file,
      'line': instance.line,
      'description': instance.description,
      'suggestedFix': instance.suggestedFix,
    };

JobLog _$JobLogFromJson(Map<String, dynamic> json) => JobLog(
      timestamp: DateTime.parse(json['timestamp'] as String),
      level: json['level'] as String,
      message: json['message'] as String,
      agent: json['agent'] as String?,
    );

Map<String, dynamic> _$JobLogToJson(JobLog instance) => <String, dynamic>{
      'timestamp': instance.timestamp.toIso8601String(),
      'level': instance.level,
      'message': instance.message,
      'agent': instance.agent,
    };

Checkpoint _$CheckpointFromJson(Map<String, dynamic> json) => Checkpoint(
      id: json['id'] as String,
      stage: json['stage'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      isRestorable: json['isRestorable'] as bool,
    );

Map<String, dynamic> _$CheckpointToJson(Checkpoint instance) =>
    <String, dynamic>{
      'id': instance.id,
      'stage': instance.stage,
      'timestamp': instance.timestamp.toIso8601String(),
      'isRestorable': instance.isRestorable,
    };

AgentStatus _$AgentStatusFromJson(Map<String, dynamic> json) => AgentStatus(
      name: json['name'] as String,
      status: json['status'] as String,
      progress: (json['progress'] as num).toInt(),
      startedAt: json['startedAt'] == null
          ? null
          : DateTime.parse(json['startedAt'] as String),
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      error: json['error'] as String?,
    );

Map<String, dynamic> _$AgentStatusToJson(AgentStatus instance) =>
    <String, dynamic>{
      'name': instance.name,
      'status': instance.status,
      'progress': instance.progress,
      'startedAt': instance.startedAt?.toIso8601String(),
      'completedAt': instance.completedAt?.toIso8601String(),
      'error': instance.error,
    };
