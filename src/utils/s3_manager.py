"""
Servicio para subir imágenes a AWS S3
"""
import boto3
import os
import logging
from fastapi import HTTPException
from datetime import datetime
import uuid
from src.utils.image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class S3Manager:
    """Gestiona la subida de archivos a AWS S3"""
    
    def __init__(self):
        """Inicializa el cliente de S3"""
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        
        if not all([self.aws_access_key, self.aws_secret_key, self.bucket_name]):
            raise HTTPException(
                status_code=500,
                detail="Configuración de AWS S3 incompleta"
            )
        
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region
        )
    
    def generate_s3_key(self, mod_id: int, image_type: str, filename: str) -> str:
        """
        Genera una clave única para el archivo en S3
        
        Formato: mods/{mod_id}/{image_type}/{timestamp}-{uuid}-{filename}.webp
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Convertir a WebP filename
        webp_filename = ImageProcessor.get_webp_filename(filename)
        # Limpiar nombre de archivo
        clean_filename = "".join(c for c in webp_filename if c.isalnum() or c in ('-', '_', '.'))
        
        return f"mods/{mod_id}/{image_type}/{timestamp}_{unique_id}_{clean_filename}"
    
    def generate_user_logo_s3_key(self, user_id: int, filename: str) -> str:
        """
        Genera una clave única para el logo de usuario en S3
        
        Formato: users/{user_id}/logo/{timestamp}-{uuid}-{filename}.webp
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Convertir a WebP filename
        webp_filename = ImageProcessor.get_webp_filename(filename)
        # Limpiar nombre de archivo
        clean_filename = "".join(c for c in webp_filename if c.isalnum() or c in ('-', '_', '.'))
        
        return f"users/{user_id}/logo/{timestamp}_{unique_id}_{clean_filename}"
    
    def upload_file(self, file_content: bytes, mod_id: int, image_type: str, filename: str) -> str:
        """
        Sube un archivo a S3 y retorna la URL pública
        
        Args:
            file_content: Contenido del archivo
            mod_id: ID del mod
            image_type: Tipo de imagen (logo, main, screenshot)
            filename: Nombre original del archivo
        
        Returns:
            URL pública de la imagen en S3
        """
        try:
            s3_key = self.generate_s3_key(mod_id, image_type, filename)
            
            logger.info(f"[S3Manager] Subiendo archivo a S3: {s3_key} (size: {len(file_content)} bytes)")
            
            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType="image/webp",
                Metadata={
                    "mod_id": str(mod_id),
                    "image_type": image_type,
                    "original_filename": filename
                }
            )
            
            logger.info(f"[S3Manager] Archivo subido exitosamente: {s3_key}")
            
            # Generar URL pública
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"[S3Manager] URL generada: {s3_url}")
            
            return s3_url
            
        except Exception as e:
            logger.error(f"[S3Manager] Error subiendo imagen a S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error subiendo imagen a S3: {str(e)}"
            )
    
    def upload_user_logo(self, file_content: bytes, user_id: int, filename: str) -> str:
        """
        Sube un logo de usuario a S3 y retorna la URL pública
        
        Args:
            file_content: Contenido del archivo
            user_id: ID del usuario
            filename: Nombre original del archivo
        
        Returns:
            URL pública del logo en S3
        """
        try:
            s3_key = self.generate_user_logo_s3_key(user_id, filename)
            
            logger.info(f"[S3Manager] Subiendo logo de usuario a S3: {s3_key} (size: {len(file_content)} bytes)")
            
            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType="image/webp",
                Metadata={
                    "user_id": str(user_id),
                    "type": "user_logo",
                    "original_filename": filename
                }
            )
            
            logger.info(f"[S3Manager] Logo de usuario subido exitosamente: {s3_key}")
            
            # Generar URL pública
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"[S3Manager] URL de logo generada: {s3_url}")
            
            return s3_url
            
        except Exception as e:
            logger.error(f"[S3Manager] Error subiendo logo de usuario a S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error subiendo logo de usuario a S3: {str(e)}"
            )
    
    def delete_file(self, file_url: str) -> bool:
        """
        Elimina un archivo de S3 basado en su URL pública
        
        Args:
            file_url: URL pública de la imagen (https://bucket.s3.region.amazonaws.com/key)
        
        Returns:
            True si se eliminó exitosamente
        """
        try:
            # Extraer la clave de S3 de la URL
            # URL: https://bucket.s3.region.amazonaws.com/path/to/key
            s3_key = file_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/", 1)[1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return True
            
        except Exception as e:
            print(f"Error eliminando imagen de S3: {str(e)}")
            return False
    
    def file_exists(self, file_url: str) -> bool:
        """Verifica si un archivo existe en S3"""
        try:
            s3_key = file_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/", 1)[1]
            
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except:
            return False
