def print_layer_weights(weights, layer_name='W2'):
    """
    Imprime los pesos de una capa específica de la red neuronal 
    para fines de diagnóstico y visualización interna.
    
    Args:
        weights (dict): Diccionario que contiene los pesos de la red.
        layer_name (str): Clave del diccionario que representa la capa a inspeccionar.
    """
    if layer_name in weights:
        print(f"--- Pesos de la capa {layer_name} ---")
        print(weights[layer_name])
    else:
        print(f"⚠️ La capa '{layer_name}' no se encontró en el diccionario de pesos.")

def print_all_weights(weights):
    """Itera e imprime todos los pesos de la red."""
    for layer, w in weights.items():
        print(f"\n[{layer}] Shape: {getattr(w, 'shape', 'N/A')}")
        print(w)

def print_neuron_weights(weights, layer_name='W1', neuron_indices=None):
    """
    Imprime los pesos de neuronas específicas dentro de una capa.
    Útil para diagnosticar cómo está aprendiendo una neurona individual.
    """
    if neuron_indices is None:
        # Por defecto muestra la neurona 1 y 2 según lo solicitado por el usuario
        neuron_indices = [1, 2]
        
    if layer_name in weights:
        print(f"\n--- Inspeccionando neuronas en la capa {layer_name} ---")
        layer_weights = weights[layer_name]
        for idx in neuron_indices:
            try:
                print(f"Pesos de la Neurona [{idx}]:\n{layer_weights[idx]}")
            except IndexError:
                print(f"⚠️ La neurona en el índice {idx} no existe en la capa {layer_name}.")
    else:
        print(f"⚠️ La capa '{layer_name}' no se encontró en el diccionario de pesos.")
