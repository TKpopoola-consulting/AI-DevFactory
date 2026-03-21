import 'package:flutter/material.dart';

class AgentSelectorWidget extends StatelessWidget {
  final Map<String, dynamic> config;
  final Function(Map<String, dynamic>) onConfigChanged;

  const AgentSelectorWidget({
    super.key,
    required this.config,
    required this.onConfigChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🤖 AGENT SELECTION',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _buildAgentCard(
                  title: 'Frontend',
                  value: config['frontend'],
                  options: const ['React', 'Flutter', 'Vue.js'],
                  onChanged: (v) => onConfigChanged({...config, 'frontend': v}),
                )),
                const SizedBox(width: 12),
                Expanded(child: _buildAgentCard(
                  title: 'Backend',
                  value: config['backend'],
                  options: const ['FastAPI', 'Django', 'Express.js'],
                  onChanged: (v) => onConfigChanged({...config, 'backend': v}),
                )),
                const SizedBox(width: 12),
                Expanded(child: _buildAgentCard(
                  title: 'Cloud',
                  value: config['cloud'],
                  options: const ['Azure', 'AWS', 'GCP'],
                  onChanged: (v) => onConfigChanged({...config, 'cloud': v}),
                )),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAgentCard({
    required String title,
    required String value,
    required List<String> options,
    required Function(String) onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          DropdownButton<String>(
            value: value,
            isExpanded: true,
            items: options.map((option) {
              return DropdownMenuItem(value: option, child: Text(option));
            }).toList(),
            onChanged: (v) => onChanged(v!),
          ),
        ],
      ),
    );
  }
}
