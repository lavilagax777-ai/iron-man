import matplotlib.pyplot as plt

def plot_predictions_vs_actuals(preds, y_test, max_val=51):
    """
    Grafica los valores predichos contra los valores reales.
    Ideal para evaluar el rendimiento de modelos de regresión.
    
    Args:
        preds: Array o lista de predicciones.
        y_test: Array o lista de valores reales.
        max_val: Valor máximo para los ejes X e Y (default 51).
    """
    plt.figure(figsize=(8, 6))
    plt.xlabel('Prediccion')
    plt.ylabel('Actual')
    
    # Ajustar dinámicamente los límites si los datos superan max_val
    limit = max(max_val, max(preds, default=max_val), max(y_test, default=max_val))
    
    plt.xlim([0, limit])
    plt.ylim([0, limit])
    
    # Puntos de datos
    plt.scatter(preds, y_test, s=2, alpha=0.7, label='Datos')
    
    # Línea ideal (Predicción perfecta: y = x)
    plt.plot([0, limit], [0, limit], c='red', linestyle='--', label='Predicción Perfecta')
    
    plt.legend()
    plt.title('Predicciones vs Valores Reales')
    plt.grid(True, alpha=0.3)
    plt.show()

