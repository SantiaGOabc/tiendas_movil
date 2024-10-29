function agregarProducto() {
    const productosContainer = document.querySelector('.productos-container');

    const nuevoProducto = document.createElement('div');
    nuevoProducto.classList.add('producto-item');
    nuevoProducto.innerHTML = `
        <div class="form-group">
            <label for="codigoProducto">Código del Producto:</label>
            <input type="text" name="codigoProducto" class="codigoProducto" required>
        </div>
        <div class="form-group">
            <label for="producto">Producto:</label>
            <input type="text" name="producto" class="producto" required>
        </div>
        <div class="form-group">
            <label for="cantidad">Cantidad:</label>
            <input type="number" name="cantidad" class="cantidad" min="1" required>
        </div>
        <div class="form-group">
            <label for="precioUnitario">Precio Unitario:</label>
            <input type="number" name="precioUnitario" class="precioUnitario" min="0" step="0.01" required>
        </div>
    `;

    productosContainer.appendChild(nuevoProducto);
}

document.querySelector('#pedidoForm').addEventListener('input', calcularTotal);

function calcularTotal() {
    const productos = document.querySelectorAll('.producto-item');
    let total = 0;

    productos.forEach(producto => {
        const cantidad = producto.querySelector('.cantidad').value;
        const precioUnitario = producto.querySelector('.precioUnitario').value;
        if (cantidad && precioUnitario) {
            total += parseFloat(cantidad) * parseFloat(precioUnitario);
        }
    });

    document.querySelector('#montoTotal').value = total.toFixed(2);
}
