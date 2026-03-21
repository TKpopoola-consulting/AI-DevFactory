import 'package:flutter/material.dart';

class OutputConfigWidget extends StatelessWidget {
  final Map<String, dynamic> config;
  final Function(Map<String, dynamic>) onConfigChanged;

  const OutputConfigWidget({
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
              '📤 OUTPUT CONFIGURATION',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('GitHub PR'),
                    value: config['github'],
                    onChanged: (v) => onConfigChanged({...config, 'github': v}),
                    dense: true,
                  ),
                ),
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('Azure Blob'),
                    value: config['blob'],
                    onChanged: (v) => onConfigChanged({...config, 'blob': v}),
                    dense: true,
                  ),
                ),
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('ZIP Download'),
                    value: config['zip'],
                    onChanged: (v) => onConfigChanged({...config, 'zip': v}),
                    dense: true,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
