#!/bin/bash
# Establece VS Code como editor por defecto (reemplaza Sublime Text)
# Ejecutar en Terminal: bash setup_vscode_default.sh

echo "Configurando VS Code como editor por defecto..."

# 1. Variables de entorno en el perfil del shell
PROFILE="$HOME/.zshrc"
[ ! -f "$PROFILE" ] && PROFILE="$HOME/.bash_profile"

# Eliminar entradas previas de Sublime y agregar VS Code
grep -v "EDITOR\|VISUAL\|subl" "$PROFILE" > /tmp/_prof_tmp && mv /tmp/_prof_tmp "$PROFILE"

cat >> "$PROFILE" << 'EOF'

# Editor por defecto: VS Code
export EDITOR="code --wait"
export VISUAL="code --wait"
EOF

echo "  -> Variables EDITOR y VISUAL actualizadas en $PROFILE"

# 2. Editor de Git
git config --global core.editor "code --wait"
echo "  -> Git: core.editor = code --wait"

# 3. Asociaciones de archivos con duti (si esta instalado)
if command -v duti &>/dev/null; then
    for ext in py js ts json md sh txt yaml yml; do
        duti -s com.microsoft.VSCode "$ext" all 2>/dev/null
    done
    echo "  -> Asociaciones de archivo actualizadas con duti"
else
    echo "  -> duti no encontrado. Para asociaciones de archivo ejecuta:"
    echo "       brew install duti"
    echo "     y vuelve a correr este script."
fi

echo ""
echo "Listo. Abre una nueva terminal o ejecuta:  source $PROFILE"
