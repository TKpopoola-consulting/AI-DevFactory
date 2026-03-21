# backend/agents/frontend_agent/utils/asset_optimizer.py
"""
Asset optimization and code splitting
"""
import re
from typing import Dict, List, Any

class AssetOptimizer:
    """Optimize generated code for performance"""
    
    def optimize_project(self, project: Dict, framework: str) -> Dict:
        """Apply optimizations to project"""
        
        # 1. Add code splitting
        project = self._add_code_splitting(project, framework)
        
        # 2. Optimize images
        project = self._optimize_images(project)
        
        # 3. Add lazy loading
        project = self._add_lazy_loading(project, framework)
        
        # 4. Minify assets
        project = self._minify_assets(project)
        
        # 5. Add performance hints
        project = self._add_performance_hints(project)
        
        return project
    
    def _add_code_splitting(self, project: Dict, framework: str) -> Dict:
        """Add code splitting configuration"""
        
        if framework == 'react':
            # Add React.lazy and Suspense
            for file in project['structure']:
                if file['path'] == 'src/App.js':
                    # Add lazy imports for routes
                    content = file['content']
                    if 'React.lazy' not in content:
                        lazy_imports = """
                        import React, { Suspense, lazy } from 'react';
                        
                        const Home = lazy(() => import('./pages/Home'));
                        const About = lazy(() => import('./pages/About'));
                        """
                        content = re.sub(
                            r'import React from \'react\';',
                            lazy_imports,
                            content
                        )
                        file['content'] = content
                    
                    # Add Suspense wrapper
                    if '<Suspense' not in content:
                        content = content.replace(
                            '<Router>',
                            '<Suspense fallback={<div>Loading...</div>}><Router></Suspense>'
                        )
                        file['content'] = content
        
        elif framework == 'vue':
            # Add Vue async components
            for file in project['structure']:
                if file['path'] == 'src/router/index.js':
                    content = file['content']
                    if '() => import' not in content:
                        # Convert routes to lazy loading
                        content = content.replace(
                            "component: Home",
                            "component: () => import('@/views/Home.vue')"
                        )
                        file['content'] = content
        
        return project
    
    def _optimize_images(self, project: Dict) -> Dict:
        """Optimize image assets"""
        # Add image optimization configuration
        config_files = []
        
        # Add next/image config if Next.js
        # Add image optimization plugin for webpack
        # Add responsive images
        
        return project
    
    def _add_lazy_loading(self, project: Dict, framework: str) -> Dict:
        """Add lazy loading for images and components"""
        
        for file in project['structure']:
            if file['path'].endswith(('.jsx', '.js', '.vue')):
                content = file['content']
                
                # Add loading="lazy" to images
                if 'loading="lazy"' not in content:
                    content = content.replace(
                        '<img',
                        '<img loading="lazy"'
                    )
                    file['content'] = content
        
        return project
    
    def _minify_assets(self, project: Dict) -> Dict:
        """Minify CSS and JS files"""
        # In production, this would use tools like terser, cssnano
        # For now, add build configuration
        
        # Add minification config to package.json
        for file in project['structure']:
            if file['path'] == 'package.json':
                pkg = json.loads(file['content'])
                pkg['scripts']['build'] = pkg.get('scripts', {}).get('build', '')
                if 'minify' not in pkg['scripts']['build']:
                    pkg['scripts']['build'] += ' && npm run minify'
                file['content'] = json.dumps(pkg, indent=2)
        
        return project
    
    def _add_performance_hints(self, project: Dict) -> Dict:
        """Add performance monitoring hints"""
        
        # Add web-vitals tracking
        web_vitals_code = """
        import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';
        
        function sendToAnalytics(metric) {
          console.log(metric);
          // Send to your analytics service
        }
        
        getCLS(sendToAnalytics);
        getFID(sendToAnalytics);
        getFCP(sendToAnalytics);
        getLCP(sendToAnalytics);
        getTTFB(sendToAnalytics);
        """
        
        # Add to main file
        for file in project['structure']:
            if file['path'] in ['src/index.js', 'src/main.js']:
                if 'web-vitals' not in file['content']:
                    file['content'] += web_vitals_code
        
        return project
