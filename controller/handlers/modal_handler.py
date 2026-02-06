
import os
import importlib.util
from pathlib import Path
import discord

class ModalHandler:
    """
    Modal handler system for controller bot
    Auto-loads modal handlers from controller/modals/ directory
    """
    
    def __init__(self):
        self.handlers = {}
    
    async def load_modals(self, bot):
        """Load all modal handlers from modals/ directory"""
        modals_dir = Path(__file__).parent.parent / "modals"
        
        if not modals_dir.exists():
            print("[ModalHandler] No modals directory found, creating...")
            modals_dir.mkdir(exist_ok=True)
            return
        
        # Walk through subdirectories
        for category_dir in modals_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('_'):
                continue
            
            for modal_file in category_dir.glob('*.py'):
                if modal_file.name.startswith('_'):
                    continue
                
                try:
                    # Import module
                    module_name = f"controller.modals.{category_dir.name}.{modal_file.stem}"
                    spec = importlib.util.spec_from_file_location(module_name, modal_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Get handler function
                    if hasattr(module, 'handler'):
                        custom_id = getattr(module, 'custom_id', modal_file.stem)
                        self.handlers[custom_id] = module.handler
                        print(f"[ModalHandler] Loaded: {custom_id}")
                        
                except Exception as e:
                    print(f"[ModalHandler] Error loading {modal_file}: {e}")
        
        print(f"[ModalHandler] Loaded {len(self.handlers)} modal handlers")
    
    async def handle_interaction(self, interaction):
        """Handle modal submission interaction"""
        custom_id = interaction.data.get('custom_id', '')
        
        # Extract base custom_id (before any |)
        base_id = custom_id.split('|')[0]
        
        if base_id in self.handlers:
            try:
                await self.handlers[base_id](interaction)
            except Exception as e:
                print(f"[ModalHandler] Error handling {custom_id}: {e}")
                import traceback
                traceback.print_exc()
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(f"Error processing modal: {e}", ephemeral=True)
                except:
                    pass
        else:
            print(f"[ModalHandler] No handler for modal: {custom_id}")

# Global instance
modal_handler = ModalHandler()
