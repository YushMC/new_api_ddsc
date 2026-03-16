"""
Servicio para procesar imágenes: redimensionar, comprimir y convertir a WebP
"""
from PIL import Image
import io
import os
from fastapi import HTTPException

class ImageProcessor:
    """Procesa imágenes: redimensiona, comprime y convierte a WebP"""
    
    # Tamaños máximos permitidos (en bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # Tipos MIME permitidos
    ALLOWED_MIMES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
    
    # Tamaño máximo de imagen en píxeles
    MAX_WIDTH = 2560
    MAX_HEIGHT = 2560
    
    @staticmethod
    def validate_image(file_content: bytes, filename: str) -> None:
        """Valida que el archivo sea una imagen válida"""
        if len(file_content) > ImageProcessor.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo muy grande. Máximo: {ImageProcessor.MAX_FILE_SIZE / (1024*1024):.0f} MB"
            )
        
        # Validar que es una imagen
        try:
            img = Image.open(io.BytesIO(file_content))
            img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="El archivo no es una imagen válida")
    
    @staticmethod
    def process_to_webp(file_content: bytes, filename: str, quality: int = 85) -> bytes:
        """
        Procesa una imagen y la convierte a WebP
        
        Args:
            file_content: Contenido del archivo de imagen
            filename: Nombre original del archivo
            quality: Calidad de compresión (1-100)
        
        Returns:
            Contenido de la imagen en formato WebP
        """
        try:
            # Abrir imagen
            img = Image.open(io.BytesIO(file_content))
            
            # Convertir a RGB si tiene transparencia (excepto PNG con alpha)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Para PNG, mantener transparencia
                if filename.lower().endswith('.png'):
                    pass
                else:
                    # Para otros formatos, convertir a RGB
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionar si es necesario
            if img.width > ImageProcessor.MAX_WIDTH or img.height > ImageProcessor.MAX_HEIGHT:
                img.thumbnail(
                    (ImageProcessor.MAX_WIDTH, ImageProcessor.MAX_HEIGHT),
                    Image.Resampling.LANCZOS
                )
            
            # Guardar como WebP
            output = io.BytesIO()
            img.save(output, format='WEBP', quality=quality, method=6)
            
            return output.getvalue()
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error procesando imagen: {str(e)}"
            )
    
    @staticmethod
    def get_webp_filename(original_filename: str) -> str:
        """Convierte el nombre del archivo a .webp"""
        name_without_ext = os.path.splitext(original_filename)[0]
        return f"{name_without_ext}.webp"
