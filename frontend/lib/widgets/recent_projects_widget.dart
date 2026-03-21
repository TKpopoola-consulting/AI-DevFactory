import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/job_provider.dart';

class RecentProjectsWidget extends StatelessWidget {
  const RecentProjectsWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final jobProvider = Provider.of<JobProvider>(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '📊 RECENT PROJECTS',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            if (jobProvider.isLoading)
              const Center(child: CircularProgressIndicator())
            else if (jobProvider.jobs.isEmpty)
              const Center(child: Text('No projects yet'))
            else
              ...jobProvider.jobs.take(3).map((job) => ListTile(
                leading: const Icon(Icons.folder),
                title: Text(job.id.substring(0, 8)),
                subtitle: Text('Status: ${job.status}'),
                trailing: TextButton(
                  onPressed: () {},
                  child: const Text('View'),
                ),
              )),
          ],
        ),
      ),
    );
  }
}
