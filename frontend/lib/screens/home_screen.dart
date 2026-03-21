// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/job_provider.dart';
import '../providers/settings_provider.dart';
import '../widgets/prompt_input_widget.dart';
import '../widgets/agent_selector_widget.dart';
import '../widgets/output_config_widget.dart';
import '../widgets/cost_estimator_widget.dart';
import '../widgets/recent_projects_widget.dart';
import '../utils/constants.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _promptController = TextEditingController();
  final _requirementController = TextEditingController();
  final List<String> _requirements = [];
  
  Map<String, dynamic> _agentConfig = {
    'frontend': 'React',
    'backend': 'FastAPI',
    'cloud': 'Azure',
    'database': 'PostgreSQL',
  };
  
  Map<String, dynamic> _outputConfig = {
    'github': true,
    'blob': false,
    'zip': true,
    'repository': '',
    'branch': 'main',
  };
  
  bool _isGenerating = false;
  
  @override
  void dispose() {
    _promptController.dispose();
    _requirementController.dispose();
    super.dispose();
  }
  
  void _addRequirement() {
    if (_requirementController.text.isNotEmpty) {
      setState(() {
        _requirements.add(_requirementController.text);
        _requirementController.clear();
      });
    }
  }
  
  void _removeRequirement(int index) {
    setState(() {
      _requirements.removeAt(index);
    });
  }
  
  Future<void> _generateApplication() async {
    if (_promptController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a prompt')),
      );
      return;
    }
    
    setState(() {
      _isGenerating = true;
    });
    
    final jobProvider = Provider.of<JobProvider>(context, listen: false);
    
    try {
      final jobId = await jobProvider.createJob(
        prompt: _promptController.text,
        config: _agentConfig,
        outputConfig: _outputConfig,
      );
      
      if (mounted) {
        Navigator.pushNamed(
          context,
          '/monitor',
          arguments: {'jobId': jobId},
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isGenerating = false;
        });
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final settings = Provider.of<SettingsProvider>(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text(AppConstants.appName),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => Navigator.pushNamed(context, '/history'),
            tooltip: 'History',
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.pushNamed(context, '/settings'),
            tooltip: 'Settings',
          ),
          IconButton(
            icon: Icon(settings.isDarkMode ? Icons.light_mode : Icons.dark_mode),
            onPressed: () => settings.toggleTheme(),
            tooltip: 'Toggle theme',
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Hero Section
            Center(
              child: Column(
                children: [
                  const Icon(
                    Icons.auto_awesome,
                    size: 48,
                    color: Color(0xFF6366F1),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Transform Ideas into Production-Ready Code',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: isDark ? Colors.white : const Color(0xFF0F172A),
                        ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Describe your application in natural language and let 4 AI agents build it in parallel',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            
            // Prompt Input
            PromptInputWidget(
              controller: _promptController,
              onEnhance: () {
                // TODO: Enhance with AI
              },
              onFileAttach: () {
                // TODO: Attach file
              },
            ),
            const SizedBox(height: 24),
            
            // Requirements Viewer
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.checklist, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          'Requirements',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const Spacer(),
                        TextButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.edit, size: 16),
                          label: const Text('Edit Mode'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    ..._requirements.asMap().entries.map((entry) {
                      final index = entry.key;
                      final req = entry.value;
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            const Icon(Icons.check_circle, size: 18, color: Colors.green),
                            const SizedBox(width: 8),
                            Expanded(child: Text(req)),
                            IconButton(
                              icon: const Icon(Icons.edit, size: 16),
                              onPressed: () {},
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete, size: 16),
                              onPressed: () => _removeRequirement(index),
                            ),
                          ],
                        ),
                      );
                    }),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _requirementController,
                            decoration: const InputDecoration(
                              hintText: 'Add a requirement...',
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            ),
                            onSubmitted: (_) => _addRequirement(),
                          ),
                        ),
                        const SizedBox(width: 8),
                        IconButton(
                          icon: const Icon(Icons.add),
                          onPressed: _addRequirement,
                          style: IconButton.styleFrom(
                            backgroundColor: Theme.of(context).primaryColor,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        TextButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.import_export),
                          label: const Text('Import from Template'),
                        ),
                        const SizedBox(width: 8),
                        TextButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.check),
                          label: const Text('Validate'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            
            // Agent Configuration
            AgentSelectorWidget(
              config: _agentConfig,
              onConfigChanged: (newConfig) {
                setState(() {
                  _agentConfig = newConfig;
                });
              },
            ),
            const SizedBox(height: 24),
            
            // Cost Estimator
            CostEstimatorWidget(
              config: _agentConfig,
              requirements: _requirements,
            ),
            const SizedBox(height: 24),
            
            // Output Configuration
            OutputConfigWidget(
              config: _outputConfig,
              onConfigChanged: (newConfig) {
                setState(() {
                  _outputConfig = newConfig;
                });
              },
            ),
            const SizedBox(height: 24),
            
            // Generate Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isGenerating ? null : _generateApplication,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: const Color(0xFF6366F1),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isGenerating
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text(
                        '🚀 GENERATE APPLICATION',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
            ),
            const SizedBox(height: 8),
            Center(
              child: Text(
                '⚡ 4 agents will run in parallel | Estimated time: 2-4 min | Cost: ~\$0.15',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
              ),
            ),
            const SizedBox(height: 24),
            
            // Recent Projects
            const RecentProjectsWidget(),
          ],
        ),
      ),
    );
  }
}
