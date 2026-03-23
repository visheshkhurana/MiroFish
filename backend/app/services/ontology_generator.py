"""

1Analyze textRelationship type
"""

import json
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient


#
ONTOLOGY_SYSTEM_PROMPT = """Knowledge graphOntology designText contentSimulation requirements**Social mediaOpinion simulation**Entity typeRelationship type

**JSON**

##
**Social mediaOpinion simulation**
- Social media""""
- 
- 

****

****
- 
- 
- NGO
- 
- 
- Social media
- 

****
- """"""
- /""""
- /""""

##
JSON

```json
{
    "entity_types": [
        {
            "name": "Entity type namePascalCase",
            "description": "100",
            "attributes": [
                {
                    "name": "snake_case",
                    "type": "text",
                    "description": ""
                }
            ],
            "examples": ["1", "2"]
        }
    ],
    "edge_types": [
        {
            "name": "Relationship type nameUPPER_SNAKE_CASE",
            "description": "100",
            "source_targets": [
                {"source": "Source entity type", "target": "Target entity type"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Brief analysis description of the text content"
}
```

##
### 1. Entity type design - 

**10Entity type**

****

10Entity type

A. **2**
   - `Person`: 
   - `Organization`: 

B. **8Text content**
   - 
   -  `Student`, `Professor`, `University`
   -  `Company`, `CEO`, `Employee`

****
- """"""
-  `Person`
-  `Organization`

****
- 
- 
- description 

### 2. Relationship type design

- 6-10
- 
-  source_targets Entity type

### 3. 

- Entity type1-3
- **** `name``uuid``group_id``created_at``summary`
- `full_name`, `title`, `role`, `position`, `location`, `description` 

## Entity type

****
- Student: 
- Professor: /
- Journalist: 
- Celebrity: /
- Executive: 
- Official: 
- Lawyer: 
- Doctor: 

****
- Person: 

****
- University: 
- Company: 
- GovernmentAgency: 
- MediaOutlet: 
- Hospital: 
- School: 
- NGO: 

****
- Organization: 

## Relationship type

- WORKS_FOR: 
- STUDIES_AT: 
- AFFILIATED_WITH: 
- REPRESENTS: 
- REGULATES: 
- REPORTS_ON: 
- COMMENTS_ON: 
- RESPONDS_TO: 
- SUPPORTS: 
- OPPOSES: 
- COLLABORATES_WITH: 
- COMPETES_WITH: 
"""


class OntologyGenerator:
    """
    
    Analyze textRelationship type
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        
        
        Args:
            document_texts: 
            simulation_requirement: Simulation requirements
            additional_context: 
            
        Returns:
            entity_types, edge_types
        """
        #
        user_message = self._build_user_message(
            document_texts, 
            simulation_requirement,
            additional_context
        )
        
        messages = [
            {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        #
        result = self._validate_and_process(result)
        
        return result
    
    #  LLM 5
    MAX_TEXT_LENGTH_FOR_LLM = 50000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """"""
        
        #
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)
        
        # 5LLM
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += f"\n\n...({original_length}{self.MAX_TEXT_LENGTH_FOR_LLM})..."
        
        message = f"""## Simulation requirements

{simulation_requirement}

##
{combined_text}
"""
        
        if additional_context:
            message += f"""
##
{additional_context}
"""
        
        message += """
Opinion simulationEntity typeRelationship type

****
1. 10Entity type
2. 2Person Organization
3. 8Text content
4. Entity type
5.  nameuuidgroup_id  full_nameorg_name 
"""
        
        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """"""
        
        #
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""
        
        # Entity type
        for entity in result["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # description100
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."
        
        # Relationship type
        for edge in result["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."
        
        # Zep API  10 Entity type 10 
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10
        
        #
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        #
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names
        
        #
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)
        
        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)
            
            #  10 
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                #
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                #
                result["entity_types"] = result["entity_types"][:-to_remove]
            
            #
            result["entity_types"].extend(fallbacks_to_add)
        
        #
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]
        
        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]
        
        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        Pythonontology.py
        
        Args:
            ontology: 
            
        Returns:
            Python
        """
        code_lines = [
            '"""',
            'Entity type',
            'MiroFishOpinion simulation',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== Entity type ==============',
            '',
        ]
        
        # Entity type
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")
            
            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        code_lines.append('# ============== Relationship type ==============')
        code_lines.append('')
        
        # Relationship type
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # PascalCase
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")
            
            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        #
        code_lines.append('# ==============  ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')
        
        # source_targets
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')
        
        return '\n'.join(code_lines)

