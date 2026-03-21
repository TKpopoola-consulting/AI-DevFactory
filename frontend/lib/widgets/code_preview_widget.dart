// lib/widgets/code_preview_widget.dart
import 'package:flutter/material.dart';
import 'package:flutter_highlight/flutter_highlight.dart';
import 'package:flutter_highlight/themes/vs2015.dart';
import '../models/job_model.dart';

class CodePreviewWidget extends StatefulWidget {
  final JobArtifacts? artifacts;
  
  const CodePreviewWidget({super.key, this.artifacts});
  
  @override
  State<CodePreviewWidget> createState() => _CodePreviewWidgetState();
}

class _CodePreviewWidgetState extends State<CodePreviewWidget> {
  String _selectedFile = '';
  String _selectedContent = '';
  
  @override
  void initState() {
    super.initState();
    _selectFirstFile();
  }
  
  void _selectFirstFile() {
    if (widget.artifacts?.files != null && widget.artifacts!.files!.isNotEmpty) {
      final firstFile = widget.artifacts!.files!.entries.first;
      setState(() {
        _selectedFile = firstFile.key;
        _selectedContent = firstFile.value;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (widget.artifacts?.files == null || widget.artifacts!.files!.isEmpty) {
      return const SizedBox.shrink();
    }
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.code, size: 20),
                SizedBox(width: 8),
                Text(
                  'Code Preview',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // File Explorer
                Container(
                  width: 250,
                  height: 400,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ListView(
                    padding: EdgeInsets.zero,
                    children: widget.artifacts!.files!.entries.map((entry) {
                      final isSelected = _selectedFile == entry.key;
                      return ListTile(
                        dense: true,
                        selected: isSelected,
                        selectedTileColor: Theme.of(context).primaryColor.withOpacity(0.1),
                        leading: Icon(
                          _getFileIcon(entry.key),
                          size: 18,
                          color: isSelected ? Theme.of(context).primaryColor : null,
                        ),
                        title: Text(
                          entry.key.split('/').last,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: isSelected ? FontWeight.bold : null,
                          ),
                        ),
                        subtitle: Text(
                          entry.key,
                          style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        onTap: () {
                          setState(() {
                            _selectedFile = entry.key;
                            _selectedContent = entry.value;
                          });
                        },
                      );
                    }).toList(),
                  ),
                ),
                const SizedBox(width: 16),
                // Code Viewer
                Expanded(
                  child: Container(
                    height: 400,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            border: Border(
                              bottom: BorderSide(color: Colors.grey.shade300),
                            ),
                          ),
                          child: Row(
                            children: [
                              Expanded(
                                child: Text(
                                  _selectedFile,
                                  style: const TextStyle(fontSize: 12),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.copy, size: 16),
                                onPressed: () {
                                  // Copy to clipboard
                                },
                                tooltip: 'Copy',
                              ),
                              IconButton(
                                icon: const Icon(Icons.download, size: 16),
                                onPressed: () {},
                                tooltip: 'Download',
                              ),
                            ],
                          ),
                        ),
                        Expanded(
                          child: SingleChildScrollView(
                            padding: const EdgeInsets.all(12),
                            child: HighlightView(
                              _selectedContent,
                              language: _getLanguage(_selectedFile),
                              theme: vs2015Theme,
                              padding: EdgeInsets.zero,
                              textStyle: const TextStyle(
                                fontFamily: 'monospace',
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Text(
                  'Total Files: ${widget.artifacts!.fileCount} | LOC: ${widget.artifacts!.linesOfCode}',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.search),
                  label: const Text('Find'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  IconData _getFileIcon(String filename) {
    if (filename.endsWith('.dart')) return Icons.code;
    if (filename.endsWith('.py')) return Icons.code;
    if (filename.endsWith('.js')) return Icons.javascript;
    if (filename.endsWith('.jsx')) return Icons.react;
    if (filename.endsWith('.json')) return Icons.data_object;
    if (filename.endsWith('.yaml') || filename.endsWith('.yml')) return Icons.settings;
    if (filename.endsWith('.md')) return Icons.description;
    if (filename.endsWith('.html')) return Icons.html;
    if (filename.endsWith('.css')) return Icons.css;
    return Icons.insert_drive_file;
  }
  
  String _getLanguage(String filename) {
    if (filename.endsWith('.dart')) return 'dart';
    if (filename.endsWith('.py')) return 'python';
    if (filename.endsWith('.js')) return 'javascript';
    if (filename.endsWith('.jsx')) return 'javascript';
    if (filename.endsWith('.json')) return 'json';
    if (filename.endsWith('.yaml') || filename.endsWith('.yml')) return 'yaml';
    if (filename.endsWith('.md')) return 'markdown';
    if (filename.endsWith('.html')) return 'html';
    if (filename.endsWith('.css')) return 'css';
    return 'plaintext';
  }
}
