import json
import re


class MetadataParser:
    def __init__(self):
        self.metadata = {
            'prompt': '',
            'negative_prompt': '',
            'seed': '',
            'steps': '',
            'cfg': '',
            'sampler_name': '',
            'model': '',
            'workflow': ''
        }
    
    def parse(self, img):
        # Check for chara data first (AI Chat Character)
        chara_data = None
        chara_raw = None
        if 'chara' in img.info:
            chara_data = img.info['chara']
            import base64
            try:
                decoded = base64.b64decode(chara_data)
                chara_raw = json.loads(decoded.decode('utf-8'))
            except:
                pass
        
        # Then check for other metadata
        if 'parameters' in img.info:
            result = self.parse_parameters(img.info['parameters'])
        elif 'prompt' in img.info:
            result = self.parse_prompt_json(img.info['prompt'])
        elif 'exif_b64' in img.info:
            # Handle base64 encoded exif data (from PNG saved by our app)
            import base64
            try:
                exif_data = base64.b64decode(img.info['exif_b64'])
                result = self.parse_exif_data(exif_data)
            except:
                result = self.parse_other_ai_image()
        elif 'exif' in img.info:
            result = self.parse_exif_data(img.info['exif'])
        elif 'AIGC' in img.info:
            result = self.parse_aigc_data(img.info['AIGC'])
        elif 'xmp' in img.info:
            result = self.parse_xmp_data(img.info['xmp'])
        elif chara_data:
            result = self.parse_chat_character(chara_data)
        else:
            result = self.parse_other_ai_image()
        
        # If chara data exists, add it to the result
        if chara_data:
            if result.get('model') != 'AI Chat Character':
                chara_result = self.parse_chat_character(chara_data)
                result['chara_workflow'] = chara_result.get('workflow', '')
            # Always save the raw chara data for editing
            if chara_raw:
                result['chara_raw'] = chara_raw
        
        return result
    
    def parse_parameters(self, parameters):
        lines = parameters.split('\n')
        self.metadata = {
            'prompt': '',
            'negative_prompt': '',
            'seed': '',
            'steps': '',
            'cfg': '',
            'sampler_name': '',
            'model': '',
            'workflow': ''
        }

        prompt_lines = []
        in_workflow = False
        workflow_lines = []

        for line in lines:
            line = line.strip()
            if not in_workflow:
                if line.startswith('Negative prompt:'):
                    self.metadata['negative_prompt'] = line.replace('Negative prompt:', '').strip()
                elif line.startswith('Steps:'):
                    parts = line.split(',')
                    for part in parts:
                        part = part.strip()
                        if part.startswith('Steps:'):
                            self.metadata['steps'] = part.replace('Steps:', '').strip()
                        elif part.startswith('CFG scale:'):
                            self.metadata['cfg'] = part.replace('CFG scale:', '').strip()
                        elif part.startswith('Sampler:'):
                            self.metadata['sampler_name'] = part.replace('Sampler:', '').strip()
                        elif part.startswith('Seed:'):
                            self.metadata['seed'] = part.replace('Seed:', '').strip()
                        elif part.startswith('Model:'):
                            self.metadata['model'] = part.replace('Model:', '').strip()
                elif line.startswith('Workflow:'):
                    in_workflow = True
                else:
                    prompt_lines.append(line)
            else:
                workflow_lines.append(line)

        self.metadata['prompt'] = '\n'.join(prompt_lines).strip()
        if workflow_lines:
            self.metadata['workflow'] = '\n'.join(workflow_lines).strip()

        return self.metadata

    def parse_prompt_json(self, prompt_data):
        self.metadata = {
            'prompt': '',
            'negative_prompt': '',
            'seed': '',
            'steps': '',
            'cfg': '',
            'sampler_name': '',
            'model': '',
            'workflow': prompt_data
        }

        try:
            workflow_data = json.loads(prompt_data)
            prompt_parts = []
            negative_parts = []
            
            for node_id, node_data in workflow_data.items():
                class_type = node_data.get('class_type', '')
                inputs = node_data.get('inputs', {})
                title = node_data.get('_meta', {}).get('title', '').lower()
                
                if class_type == 'Text Multiline':
                    text = inputs.get('text', '')
                    if text:
                        if isinstance(text, list):
                            text = ' '.join(map(str, text))
                        prompt_parts.append(text)
                
                elif class_type == 'CLIPTextEncode':
                    text = inputs.get('text', '')
                    if text:
                        if isinstance(text, list):
                            text = ' '.join(map(str, text))
                        if 'negative' in title:
                            negative_parts.append(text)
                        elif 'positive' in title or not negative_parts:
                            prompt_parts.append(text)
                
                elif class_type in ('CLIPTextEncodeSDXL', 'CLIPTextEncodeSDXLRefiner'):
                    text_g = inputs.get('text_g', '')
                    text_l = inputs.get('text_l', '')
                    if text_g:
                        if isinstance(text_g, list):
                            text_g = ' '.join(map(str, text_g))
                        prompt_parts.append(text_g)
                    if text_l:
                        if isinstance(text_l, list):
                            text_l = ' '.join(map(str, text_l))
                        prompt_parts.append(text_l)

            if prompt_parts:
                self.metadata['prompt'] = '\n'.join(prompt_parts)
            if negative_parts:
                self.metadata['negative_prompt'] = '\n'.join(negative_parts)

            for node_id, node_data in workflow_data.items():
                class_type = node_data.get('class_type', '')
                inputs = node_data.get('inputs', {})
                
                if class_type in ('KSampler', 'KSamplerAdvanced'):
                    self.metadata['seed'] = str(inputs.get('seed', inputs.get('noise_seed', '')))
                    self.metadata['steps'] = str(inputs.get('steps', ''))
                    self.metadata['cfg'] = str(inputs.get('cfg', ''))
                    self.metadata['sampler_name'] = str(inputs.get('sampler_name', ''))
                elif class_type in ('UNETLoader', 'CheckpointLoaderSimple'):
                    model_name = inputs.get('unet_name', inputs.get('ckpt_name', ''))
                    if model_name:
                        if isinstance(model_name, list):
                            model_name = str(model_name)
                        self.metadata['model'] = model_name.split('\\')[-1]
        except json.JSONDecodeError:
            pass

        return self.metadata

    def parse_exif_data(self, exif_data):
        self.metadata = {
            'prompt': '',
            'negative_prompt': '',
            'seed': '',
            'steps': '',
            'cfg': '',
            'sampler_name': '',
            'model': '',
            'workflow': ''
        }
        
        try:
            unicode_index = exif_data.find(b'UNICODE')
            if unicode_index == -1:
                encodings = ['utf-8', 'utf-16', 'utf-16-be', 'utf-16-le', 'latin-1']
                best_exif_str = ''
                for encoding in encodings:
                    try:
                        exif_str = exif_data.decode(encoding, errors='ignore')
                        if exif_str and len(exif_str) > len(best_exif_str):
                            best_exif_str = exif_str
                    except:
                        continue
                
                exif_str = best_exif_str
                
                if exif_str:
                    exif_str = ''.join(c for c in exif_str if c.isprintable() or c in '\n\t')
                    self.metadata['workflow'] = f"原始EXIF数据: {exif_str[:500]}"
                    
                    prompt_match = re.search(r'prompt[:=]\s*(.+)', exif_str, re.IGNORECASE)
                    if prompt_match:
                        self.metadata['prompt'] = prompt_match.group(1).strip()
                    else:
                        lines = exif_str.split('\n')
                        long_lines = [line.strip() for line in lines if len(line.strip()) > 20]
                        if long_lines:
                            self.metadata['prompt'] = max(long_lines, key=len)
                        else:
                            prompt_lines = []
                            for line in lines:
                                line = line.strip()
                                if line and not any(keyword in line for keyword in ['Steps:', 'CFG scale:', 'Seed:', 'Sampler:', 'Model:', 'Negative']):
                                    prompt_lines.append(line)
                            if prompt_lines:
                                self.metadata['prompt'] = ' '.join(prompt_lines)
                            else:
                                self.metadata['prompt'] = exif_str[:500]
                    
                    negative_match = re.search(r'negative[:=]\s*(.+)', exif_str, re.IGNORECASE)
                    if negative_match:
                        self.metadata['negative_prompt'] = negative_match.group(1).strip()
                    else:
                        negative_match = re.search(r'Negative\s+prompt[:=]\s*(.+)', exif_str, re.IGNORECASE)
                        if negative_match:
                            self.metadata['negative_prompt'] = negative_match.group(1).strip()
                    
                    if 'Steps:' in exif_str:
                        match = re.search(r'Steps:\s*(\d+)', exif_str)
                        self.metadata['steps'] = match.group(1) if match else ''
                    if 'CFG scale:' in exif_str:
                        match = re.search(r'CFG scale:\s*([\d.]+)', exif_str)
                        self.metadata['cfg'] = match.group(1) if match else ''
                    if 'Seed:' in exif_str:
                        match = re.search(r'Seed:\s*(\d+)', exif_str)
                        self.metadata['seed'] = match.group(1) if match else ''
                    if 'Sampler:' in exif_str:
                        match = re.search(r'Sampler:\s*([^,]+)', exif_str)
                        self.metadata['sampler_name'] = match.group(1) if match else ''
                    if 'Model:' in exif_str:
                        match = re.search(r'Model:\s*([^,]+)', exif_str)
                        self.metadata['model'] = match.group(1) if match else ''
                else:
                    self.metadata['prompt'] = 'Unable to parse prompt'
                    self.metadata['workflow'] = 'Unable to parse EXIF data'
            else:
                unicode_data = exif_data[unicode_index + 8:]
                decoded = None
                
                def count_ascii(s):
                    return sum(1 for c in s if ord(c) < 128)
                
                best_decoded = None
                best_ascii_count = 0
                
                for encoding in ['utf-16-be', 'utf-16-le', 'utf-16']:
                    try:
                        test_decoded = unicode_data.decode(encoding)
                        ascii_count = count_ascii(test_decoded)
                        if ascii_count > best_ascii_count:
                            best_ascii_count = ascii_count
                            best_decoded = test_decoded
                    except:
                        continue
                
                if best_decoded:
                    decoded = best_decoded
                else:
                    decoded = unicode_data.decode('utf-16', errors='ignore')
                
                exif_str = ''.join(c for c in decoded if c.isprintable() or c in '\n\t')
                lines = exif_str.split('\n')
                
                prompt_lines = []
                negative_prompt_lines = []
                params_lines = []
                current_section = 'prompt'
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if 'Negative' in line:
                        current_section = 'negative_prompt'
                        negative_prompt = line.split('Negative', 1)[1].strip()
                        if negative_prompt:
                            negative_prompt_lines.append(negative_prompt)
                    elif line.startswith('Steps:'):
                        current_section = 'params'
                        params_lines.append(line)
                    elif current_section == 'prompt':
                        prompt_lines.append(line)
                    elif current_section == 'negative_prompt':
                        negative_prompt_lines.append(line)
                    elif current_section == 'params':
                        params_lines.append(line)
                
                self.metadata['prompt'] = ' '.join(prompt_lines).strip()
                self.metadata['negative_prompt'] = ' '.join(negative_prompt_lines).strip()
                
                if params_lines:
                    params_text = ' '.join(params_lines)
                    self.metadata['workflow'] = params_text
                    
                    if 'Steps:' in params_text:
                        self.metadata['steps'] = params_text.split('Steps:')[1].split(',')[0].strip()
                    if 'CFG scale:' in params_text:
                        self.metadata['cfg'] = params_text.split('CFG scale:')[1].split(',')[0].strip()
                    if 'Seed:' in params_text:
                        self.metadata['seed'] = params_text.split('Seed:')[1].split(',')[0].strip()
                    if 'Sampler:' in params_text:
                        self.metadata['sampler_name'] = params_text.split('Sampler:')[1].split(',')[0].strip()
                    if 'Model:' in params_text:
                        self.metadata['model'] = params_text.split('Model:')[1].split(',')[0].strip()
            
            if not self.metadata['prompt'] or len(self.metadata['prompt']) < 5:
                if self.metadata['workflow']:
                    workflow_str = self.metadata['workflow']
                    lines = workflow_str.split('\n')
                    long_lines = [line.strip() for line in lines if len(line.strip()) > 20]
                    if long_lines:
                        self.metadata['prompt'] = max(long_lines, key=len)
                    else:
                        non_param_lines = [line.strip() for line in lines if not any(keyword in line for keyword in ['Steps:', 'CFG scale:', 'Seed:', 'Sampler:', 'Model:'])]
                        if non_param_lines:
                            self.metadata['prompt'] = ' '.join(non_param_lines)
                        else:
                            self.metadata['prompt'] = 'Unable to parse prompt'
        except Exception as e:
            self.metadata = {
                'prompt': 'Unable to parse prompt',
                'negative_prompt': '',
                'seed': '',
                'steps': '',
                'cfg': '',
                'sampler_name': '',
                'model': '',
                'workflow': f'Error parsing EXIF data: {str(e)}'
            }

        return self.metadata

    def parse_aigc_data(self, aigc_data):
        self.metadata = {
            'prompt': 'None',
            'negative_prompt': 'None',
            'seed': 'None',
            'steps': 'None',
            'cfg': 'None',
            'sampler_name': 'None',
            'model': 'Doubao',
            'workflow': ''
        }
        
        try:
            aigc_info = json.loads(aigc_data)
            self.metadata['workflow'] = "Doubao AI Info:\n"
            for key, value in aigc_info.items():
                self.metadata['workflow'] += f"{key}: {value}\n"
        except Exception:
            pass

        return self.metadata

    def parse_xmp_data(self, xmp_data):
        self.metadata = {
            'prompt': 'None',
            'negative_prompt': 'None',
            'seed': 'None',
            'steps': 'None',
            'cfg': 'None',
            'sampler_name': 'None',
            'model': 'Qwen Image',
            'workflow': ''
        }
        
        try:
            xmp_str = xmp_data.decode('utf-8', errors='ignore')
            aigc_match = re.search(r'TC260:AIGC="(.*?)"', xmp_str)
            if aigc_match:
                aigc_json = aigc_match.group(1)
                aigc_json = aigc_json.replace('&quot;', '"')
                try:
                    aigc_info = json.loads(aigc_json)
                    self.metadata['workflow'] = "Qwen Image AI Info:\n"
                    for key, value in aigc_info.items():
                        self.metadata['workflow'] += f"{key}: {value}\n"
                except:
                    self.metadata['workflow'] = f"XMP Data: {xmp_str[:500]}..."
            else:
                self.metadata['workflow'] = f"XMP Data: {xmp_str[:500]}..."
        except Exception:
            pass

        return self.metadata

    def parse_chat_character(self, chara_data):
        self.metadata = {
            'prompt': 'AI Chat Character',
            'negative_prompt': 'None',
            'seed': 'None',
            'steps': 'None',
            'cfg': 'None',
            'sampler_name': 'None',
            'model': 'AI Chat Character',
            'workflow': ''
        }
        
        try:
            # Try to decode base64 if it looks like base64
            import base64
            
            # Check if it's base64 encoded
            if chara_data and chara_data[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=':
                try:
                    decoded = base64.b64decode(chara_data)
                    chara_data = decoded.decode('utf-8')
                except:
                    pass
            
            chara_info = json.loads(chara_data)
            self.metadata['workflow'] = "AI Chat Character Info:\n"
            self.metadata['workflow'] += f"Name: {chara_info.get('name', 'Unknown')}\n"
            self.metadata['workflow'] += f"Description: {chara_info.get('description', '')}\n"
            
            first_mes = chara_info.get('first_mes', '')
            if first_mes:
                self.metadata['workflow'] += f"First Message: {first_mes}\n"
            
            scenario = chara_info.get('scenario', '')
            if scenario:
                self.metadata['workflow'] += f"Scenario: {scenario}\n"
            
            create_date = chara_info.get('create_date', '')
            if create_date:
                self.metadata['workflow'] += f"Create Date: {create_date}\n"
            
            personality = chara_info.get('personality', '')
            if personality:
                self.metadata['workflow'] += f"Personality: {personality}\n"
        except Exception as e:
            self.metadata['workflow'] = f"Error parsing chat character: {str(e)}"
        
        return self.metadata

    def parse_other_ai_image(self):
        self.metadata = {
            'prompt': 'None',
            'negative_prompt': 'None',
            'seed': 'None',
            'steps': 'None',
            'cfg': 'None',
            'sampler_name': 'None',
            'model': 'Unknown AI Tool',
            'workflow': 'No metadata found'
        }
        return self.metadata
