import 'package:flutter/material.dart';

class PromptInputWidget extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onEnhance;
  final VoidCallback onFileAttach;

  const PromptInputWidget({
    super.key,
    required this.controller,
    required this.onEnhance,
    required this.onFileAttach,
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
              '📝 PROMPT INPUT',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: controller,
              maxLines: 6,
              decoration: const InputDecoration(
                hintText: 'Describe your application...',
                border: OutlineInputBorder(),
                filled: true,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                TextButton.icon(
                  onPressed: onEnhance,
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Enhance with AI'),
                ),
                const SizedBox(width: 8),
                TextButton.icon(
                  onPressed: onFileAttach,
                  icon: const Icon(Icons.attach_file),
                  label: const Text('Attach File'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
