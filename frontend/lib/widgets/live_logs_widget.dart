// lib/widgets/live_logs_widget.dart
import 'package:flutter/material.dart';
import '../models/job_model.dart';

class LiveLogsWidget extends StatefulWidget {
  final List<JobLog> logs;
  
  const LiveLogsWidget({super.key, required this.logs});
  
  @override
  State<LiveLogsWidget> createState() => _LiveLogsWidgetState();
}

class _LiveLogsWidgetState extends State<LiveLogsWidget> {
  final ScrollController _scrollController = ScrollController();
  bool _autoScroll = true;
  String _filter = 'all';
  
  @override
  void initState() {
    super.initState();
    _scrollToBottom();
  }
  
  @override
  void didUpdateWidget(LiveLogsWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.logs.length != oldWidget.logs.length && _autoScroll) {
      _scrollToBottom();
    }
  }
  
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
  
  List<JobLog> get _filteredLogs {
    if (_filter == 'all') return widget.logs;
    if (_filter == 'error') return widget.logs.where((l) => l.level == 'error').toList();
    if (_filter == 'warning') return widget.logs.where((l) => l.level == 'warning').toList();
    if (_filter == 'info') return widget.logs.where((l) => l.level == 'info').toList();
    return widget.logs;
  }
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.terminal, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Live Logs',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                // Filter chips
                _buildFilterChip('All', 'all'),
                const SizedBox(width: 4),
                _buildFilterChip('Errors', 'error'),
                const SizedBox(width: 4),
                _buildFilterChip('Warnings', 'warning'),
                const SizedBox(width: 4),
                _buildFilterChip('Info', 'info'),
                const SizedBox(width: 8),
                IconButton(
                  icon: Icon(
                    _autoScroll ? Icons.vertical_align_bottom : Icons.vertical_align_center,
                    size: 18,
                  ),
                  onPressed: () {
                    setState(() {
                      _autoScroll = !_autoScroll;
                      if (_autoScroll) _scrollToBottom();
                    });
                  },
                  tooltip: _autoScroll ? 'Auto-scroll on' : 'Auto-scroll off',
                ),
                IconButton(
                  icon: const Icon(Icons.download, size: 18),
                  onPressed: () {},
                  tooltip: 'Download logs',
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              height: 300,
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(12),
                itemCount: _filteredLogs.length,
                itemBuilder: (context, index) {
                  final log = _filteredLogs[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${log.timestamp.hour.toString().padLeft(2, '0')}:${log.timestamp.minute.toString().padLeft(2, '0')}:${log.timestamp.second.toString().padLeft(2, '0')}',
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 11,
                            color: Colors.grey,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          width: 60,
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                          decoration: BoxDecoration(
                            color: log.levelColor.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            log.level.toUpperCase(),
                            style: TextStyle(
                              fontSize: 10,
                              color: log.levelColor,
                              fontWeight: FontWeight.bold,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            log.message,
                            style: const TextStyle(
                              fontFamily: 'monospace',
                              fontSize: 11,
                              color: Colors.white,
                            ),
                          ),
                        ),
                        if (log.agent != null)
                          Padding(
                            padding: const EdgeInsets.only(left: 8),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.blue.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                log.agent!,
                                style: const TextStyle(
                                  fontSize: 10,
                                  color: Colors.blue,
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildFilterChip(String label, String value) {
    return FilterChip(
      label: Text(label),
      selected: _filter == value,
      onSelected: (selected) {
        setState(() {
          _filter = value;
        });
      },
      showCheckmark: false,
      backgroundColor: Colors.transparent,
      selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
      labelStyle: TextStyle(
        color: _filter == value ? Theme.of(context).primaryColor : null,
      ),
    );
  }
}
