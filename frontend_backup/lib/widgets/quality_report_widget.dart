// lib/widgets/quality_report_widget.dart
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/job_model.dart';

class QualityReportWidget extends StatelessWidget {
  final JobQuality quality;
  
  const QualityReportWidget({super.key, required this.quality});
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.assessment, size: 20),
                SizedBox(width: 8),
                Text(
                  'Quality Report',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Overall Score
            Row(
              children: [
                Expanded(
                  child: _buildScoreCard(
                    context,
                    'Overall',
                    quality.overall,
                    _getGrade(quality.overall),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildScoreCard(
                    context,
                    'Security',
                    quality.security,
                    _getGrade(quality.security),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildScoreCard(
                    context,
                    'Tests',
                    quality.tests,
                    _getGrade(quality.tests),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildScoreCard(
                    context,
                    'Coverage',
                    quality.coverage,
                    _getGrade(quality.coverage),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildScoreCard(
                    context,
                    'Performance',
                    quality.performance,
                    _getGrade(quality.performance),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 12),
            // Issues
            if (quality.issues.isNotEmpty) ...[
              const Text(
                'Issues Found',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...quality.issues.map((issue) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: issue.severityColor,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                issue.title,
                                style: const TextStyle(fontSize: 14),
                              ),
                              if (issue.description.isNotEmpty)
                                Text(
                                  issue.description,
                                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                                ),
                            ],
                          ),
                        ),
                        if (issue.suggestedFix != null)
                          TextButton(
                            onPressed: () {},
                            child: const Text('Fix'),
                          ),
                      ],
                    ),
                  )),
              const SizedBox(height: 12),
            ],
            // Recommendations
            if (quality.recommendations.isNotEmpty) ...[
              const Text(
                'Recommendations',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...quality.recommendations.map((rec) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      children: [
                        const Icon(Icons.lightbulb, size: 16, color: Colors.orange),
                        const SizedBox(width: 8),
                        Expanded(child: Text(rec)),
                      ],
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildScoreCard(BuildContext context, String label, double score, String grade) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _getScoreColor(score).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
          ),
          const SizedBox(height: 4),
          Text(
            '${score.toStringAsFixed(0)}',
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            grade,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: _getScoreColor(score),
            ),
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: score / 100,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(_getScoreColor(score)),
          ),
        ],
      ),
    );
  }
  
  String _getGrade(double score) {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  }
  
  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }
}
