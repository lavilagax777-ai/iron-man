# ROADMAP Y REGLAS DEL PROYECTO

Este documento define la dirección técnica a largo plazo y las reglas estrictas de arquitectura para el ecosistema "Iron Man" y las aplicaciones de negocio (SaaS).

## REGLAS DE ARQUITECTURA (Architecture Guidelines)

1. **Base de Datos:** 
   - ESTRICTAMENTE prohibido usar Supabase para este proyecto de negocio. 
   - Toda la persistencia de datos (catálogos, inventarios) usará **Firebase** (Firestore para datos, Storage para imágenes).
   - Supabase queda reservado únicamente para los proyectos personales del desarrollador y no debe mencionarse en el código de las aplicaciones de negocio.

2. **Flujo de Datos con IA:** 
   - La aplicación debe extraer los datos crudos de Firebase.
   - Esos datos se pasan por el modelo de lenguaje (LLM) para que los analice/filtre/combine.
   - El resultado útil se mostrará en el dashboard o se re-escribirá en Firebase según sea necesario.

## ROADMAP (Próximos Pasos)

- **Fase Actual:** Conectar la aplicación Premium de Inventario (creada en Google AI Studio) con Firebase.
- **Fase Siguiente:** Desarrollar el sistema de Marketing basado en IA que analice los datos de Firestore.
- **Fase Futura:** Integración de Pagos (Stripe/MercadoPago) aislada del Centro de Mando.
