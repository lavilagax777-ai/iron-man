import sys
import os

# Agregamos la ruta del proyecto al path para poder importar las utilidades
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.debug import print_layer_weights
from utils.metrics import evaluate_and_print_metrics
from utils.data_viz import plot_predictions_vs_actuals

def evaluate_network_pipeline(X_test, y_test, weights, predecirRed_func):
    """
    Ejecuta el flujo completo de evaluación post-entrenamiento de la red:
    1. Inspecciona los pesos (W2)
    2. Realiza predicciones
    3. Calcula e imprime errores (MAE, RMSE)
    4. Grafica resultados
    """
    print("\n" + "="*40)
    print("1. INSPECCIÓN DE PESOS")
    print("="*40)
    # Vemos los pesos de la segunda capa
    print_layer_weights(weights, layer_name='W2')
    
    print("\n" + "="*40)
    print("2. PREDICCIONES Y ERRORES")
    print("="*40)
    # Hacemos las predicciones con el test set
    preds = predecirRed_func(X_test, weights)
    
    # Calculamos los errores
    evaluate_and_print_metrics(preds, y_test)
    
    print("\n" + "="*40)
    print("3. VISUALIZACIÓN")
    print("="*40)
    # Graficamos la comparativa
    plot_predictions_vs_actuals(preds, y_test)
    
    return preds
