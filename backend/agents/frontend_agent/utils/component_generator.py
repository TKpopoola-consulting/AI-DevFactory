# backend/agents/frontend_agent/utils/component_generator.py
"""
Advanced component generation with hierarchy and styling
"""
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class ComponentType(Enum):
    PAGE = "page"
    LAYOUT = "layout"
    COMPONENT = "component"
    ATOMIC = "atomic"

@dataclass
class Component:
    """Component definition with props and state"""
    name: str
    type: ComponentType
    props: List[Dict[str, Any]]
    state: List[Dict[str, Any]]
    children: List['Component']
    styling: Dict[str, str]
    imports: List[str]

class ComponentHierarchyGenerator:
    """Generate component tree from requirements"""
    
    def __init__(self, framework: str):
        self.framework = framework
        self.components: Dict[str, Component] = {}
    
    def generate_hierarchy(self, prompt: str) -> Dict[str, Component]:
        """Generate component hierarchy from natural language"""
        
        # Extract component requirements
        components = self._extract_components(prompt)
        
        # Build dependency tree
        hierarchy = self._build_tree(components)
        
        # Generate each component
        for comp in hierarchy.values():
            self._generate_component_code(comp)
        
        return hierarchy
    
    def _extract_components(self, prompt: str) -> List[Component]:
        """Extract component list from prompt"""
        # Use Gemini to identify components
        extraction_prompt = f"""
        Analyze this app requirement and list all necessary components:
        {prompt}
        
        Return as JSON:
        {{
            "components": [
                {{
                    "name": "ComponentName",
                    "type": "page|layout|component",
                    "description": "..."
                }}
            ]
        }}
        """
        
        # This would call Gemini to extract components
        # For now, return empty list
        return []
    
    def _build_tree(self, components: List[Component]) -> Dict[str, Component]:
        """Build component dependency tree"""
        hierarchy = {}
        
        for comp in components:
            hierarchy[comp.name] = comp
            comp.children = self._find_children(comp.name, components)
        
        return hierarchy
    
    def _find_children(self, parent_name: str, components: List[Component]) -> List[Component]:
        """Find child components for a parent"""
        # Logic to determine parent-child relationships
        return []
    
    def _generate_component_code(self, component: Component) -> str:
        """Generate code for a component based on framework"""
        if self.framework == 'react':
            return self._generate_react_component(component)
        elif self.framework == 'vue':
            return self._generate_vue_component(component)
        elif self.framework == 'flutter':
            return self._generate_flutter_widget(component)
    
    def _generate_react_component(self, component: Component) -> str:
        """Generate React component with proper structure"""
        props = self._generate_props_interface(component.props)
        state = self._generate_state_hooks(component.state)
        children = self._render_children(component.children)
        
        return f"""
        import React{', useState, useEffect' if state else ''} from 'react';
        {component.imports}
        
        {props}
        
        export const {component.name} = ({self._format_props(component.props)}) => {{
            {state}
            
            return (
                <div className="{component.styling.get('container', '')}">
                    {children}
                </div>
            );
        }};
        """
    
    def _generate_vue_component(self, component: Component) -> str:
        """Generate Vue 3 component with Composition API"""
        return f"""
        <template>
            <div class="{component.styling.get('container', '')}">
                {self._render_vue_children(component.children)}
            </div>
        </template>
        
        <script setup>
        {self._generate_vue_imports(component)}
        {self._generate_vue_props(component.props)}
        {self._generate_vue_state(component.state)}
        </script>
        
        <style scoped>
        {self._generate_css(component.styling)}
        </style>
        """
    
    def _generate_flutter_widget(self, component: Component) -> str:
        """Generate Flutter widget with proper structure"""
        return f"""
        import 'package:flutter/material.dart';
        
        class {component.name} extends {self._get_widget_type(component)} {{
            {self._generate_flutter_props(component.props)}
            
            @override
            Widget build(BuildContext context) {{
                return Container(
                    {self._generate_flutter_styling(component.styling)},
                    child: Column(
                        children: [
                            {self._render_flutter_children(component.children)}
                        ],
                    ),
                );
            }}
        }}
        """
    
    def _generate_props_interface(self, props: List[Dict]) -> str:
        """Generate TypeScript interface for props"""
        if not props:
            return ""
        
        prop_defs = "\n    ".join([f"{p['name']}: {p['type']};" for p in props])
        return f"""
        interface {self._get_component_name()}Props {{
            {prop_defs}
        }}
        """


class StylingGenerator:
    """Generate styling for components"""
    
    def __init__(self, framework: str, library: str = 'tailwind'):
        self.framework = framework
        self.library = library
    
    def generate_styling(self, component_desc: str) -> Dict[str, str]:
        """Generate styling for a component"""
        
        if self.library == 'tailwind':
            return self._generate_tailwind_styles(component_desc)
        elif self.library == 'styled-components':
            return self._generate_styled_components(component_desc)
        elif self.library == 'css-modules':
            return self._generate_css_modules(component_desc)
        else:
            return self._generate_inline_styles(component_desc)
    
    def _generate_tailwind_styles(self, component_desc: str) -> Dict[str, str]:
        """Generate Tailwind CSS classes"""
        style_map = {
            'container': 'container mx-auto px-4',
            'card': 'bg-white rounded-lg shadow-md p-6',
            'button': 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded',
            'input': 'border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'flex': 'flex items-center',
            'grid': 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4',
        }
        
        # Determine appropriate classes based on description
        classes = {}
        if 'card' in component_desc.lower():
            classes['container'] = style_map['card']
        if 'button' in component_desc.lower():
            classes['button'] = style_map['button']
        
        return classes
    
    def _generate_styled_components(self, component_desc: str) -> Dict[str, str]:
        """Generate styled-components"""
        return {
            'styled': f"""
            import styled from 'styled-components';
            
            export const Container = styled.div`
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 1rem;
            `;
            
            export const Card = styled.div`
                background: white;
                border-radius: 0.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 1.5rem;
            `;
            """
        }
    
    def _generate_css_modules(self, component_desc: str) -> Dict[str, str]:
        """Generate CSS modules"""
        return {
            'css': f"""
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 1rem;
            }}
            
            .card {{
                background: white;
                border-radius: 0.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 1.5rem;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 0 0.5rem;
                }}
            }}
            """
        }
    
    def _generate_inline_styles(self, component_desc: str) -> Dict[str, str]:
        """Generate inline styles"""
        return {
            'container': 'maxWidth: "1200px", margin: "0 auto", padding: "0 16px"',
            'card': 'backgroundColor: "white", borderRadius: "8px", boxShadow: "0 4px 6px rgba(0,0,0,0.1)", padding: "24px"'
        }
