import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/job_provider.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final jobProvider = Provider.of<JobProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Job History'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: jobProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : jobProvider.jobs.isEmpty
              ? const Center(child: Text('No jobs yet'))
              : ListView.builder(
                  itemCount: jobProvider.jobs.length,
                  itemBuilder: (context, index) {
                    final job = jobProvider.jobs[index];
                    return ListTile(
                      leading: Icon(
                        job.status == 'completed' ? Icons.check_circle : Icons.hourglass_empty,
                        color: job.status == 'completed' ? Colors.green : Colors.orange,
                      ),
                      title: Text(job.id.substring(0, 8)),
                      subtitle: Text('Status: ${job.status} | ${job.createdAt}'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {},
                    );
                  },
                ),
    );
  }
}
