
import discord
import os
import importlib.util
from pathlib import Path

class ButtonHandler:
    def __init__(self):
        self.button_handlers = {}
        
    async def load_buttons(self, bot):
        buttons_dir = Path(__file__).parent.parent / "buttons"
        
        if not buttons_dir.exists():
            print("[ButtonHandler] Buttons directory not found.")
            return

        count = 0
        for root, dirs, files in os.walk(buttons_dir):
            if "__pycache__" in root: continue
            
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    try:
                        file_path = Path(root) / file
                        # Construct module name relative to controller
                        # controller.buttons.subdir.file
                        rel_path = file_path.relative_to(buttons_dir.parent).with_suffix('')
                        module_name = "controller." + ".".join(rel_path.parts)
                        
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'handler'):
                            # Use custom_id variable if present, else filename
                            c_id = getattr(module, 'custom_id', file_path.stem)
                            self.button_handlers[c_id] = module.handler
                            count += 1
                            
                    except Exception as e:
                        print(f"[ButtonHandler] Error loading {file}: {e}")
                        
        print(f"[ButtonHandler] Loaded {count} button handlers.")

    async def handle_interaction(self, interaction):
        custom_id = interaction.data.get('custom_id', '')
        # Handle prefix-based routing (e.g. "guide_action|starting_bot")
        # Check if full ID matches first
        handler = self.button_handlers.get(custom_id)
        
        # If not, try splitting by |
        if not handler and '|' in custom_id:
            prefix = custom_id.split('|')[0]
            handler = self.button_handlers.get(prefix)
            
        if handler:
            try:
                await handler(interaction)
            except Exception as e:
                print(f"[ButtonHandler] Error in {custom_id}: {e}")
                # Try to tell user
                try: 
                    if not interaction.response.is_done():
                        await interaction.response.send_message("❌ Error executing button.", ephemeral=True)
                except: pass
        else:
            # Silent fail or debug
            # print(f"[ButtonHandler] No handler for {custom_id}")
            pass

button_handler = ButtonHandler()
