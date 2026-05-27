import numpy as np

def mae(preds, y_test):
    """Mean Absolute Error"""
    return np.mean(np.abs(np.array(preds) - np.array(y_test)))

def rmse(preds, y_test):
    """Root Mean Squared Error"""
    return np.sqrt(np.mean((np.array(preds) - np.array(y_test)) ** 2))

def evaluate_and_print_metrics(preds, y_test):
    """
    Calcula y muestra en consola las métricas de error MAE y RMSE.
    """
    print('MAE:', round(mae(preds, y_test), 4))
    print('RMSE:', round(rmse(preds, y_test), 4))

def pipeline_evaluacion_red(X_test, y_test, weights, model_predict_func):
    """
    Reproduce el flujo exacto proporcionado:
    hace predicciones con el test set y calcula errores.
    """
    # 1. Hacemos las predicciones con el test set
    preds = model_predict_func(X_test, weights)
    
    # 2. Calculamos y mostramos los errores
    evaluate_and_print_metrics(preds, y_test)
    
    return preds
