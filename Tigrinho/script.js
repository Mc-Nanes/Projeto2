const ICONS = [
    'apple', 'apricot', 'banana', 'big_win', 'cherry', 'grapes', 'lemon', 'lucky_seven', 'orange', 'pear', 'strawberry', 'watermelon',
];

/**
 * @type {number} Spin minimo
 */
const BASE_SPINNING_DURATION = 2.7;

/**
 * @type {number} Duracao adicional de cada spin
 * Animacao de efeito cascata nos resultados
 */
const COLUMN_SPINNING_DURATION = 0.3;


var cols;


window.addEventListener('DOMContentLoaded', function(event) {
    cols = document.querySelectorAll('.col');

    setInitialItems();
});

function setInitialItems() {
    let baseItemAmount = 40;

    for (let i = 0; i < cols.length; ++i) {
        let col = cols[i];
        let amountOfItems = baseItemAmount + (i * 3); // Valor de coluna
        let elms = '';
        let firstThreeElms = '';

        for (let x = 0; x < amountOfItems; x++) {
            let icon = getRandomIcon();
            let item = '<div class="icon" data-item="' + icon + '"><img src="items/' + icon + '.png"></div>';
            elms += item;

            if (x < 3) firstThreeElms += item; // Salva os 3 primeiros valores pois os ultimos são iguais
        }
        col.innerHTML = elms + firstThreeElms;
    }
}

/**
 * Começar quando aperta o botão
 *
 * @param elem botão
 */
function spin(elem) {
    let duration = BASE_SPINNING_DURATION + randomDuration();

    for (let col of cols) { // Definir animacao de cada coluna
        duration += COLUMN_SPINNING_DURATION + randomDuration();
        col.style.animationDuration = duration + "s";
    }

    // Impedir rolagem infinita
    elem.setAttribute('disabled', true);

    // Juntar CSS com Java
    document.getElementById('container').classList.add('spinning');

    // delay dos resultados
    //(CHAMAR O SERVIDOR AQUI PARA O RESULTADO)
    window.setTimeout(setResult, BASE_SPINNING_DURATION * 1000 / 2);

    window.setTimeout(function () {
        // quando terminar a rodada liberar o botão para começar novamente
        document.getElementById('container').classList.remove('spinning');
        elem.removeAttribute('disabled');
    }.bind(elem), duration * 1000);
}

/**
 * botar os resultados nas colunas no começo e fim
 */
function setResult() {
    for (let col of cols) {

        //gerar 3 icones aleatorios
        let results = [
            getRandomIcon(),
            getRandomIcon(),
            getRandomIcon()
        ];

        let icons = col.querySelectorAll('.icon img');
        //Demonstrar itens do resultado na tela para parecer q foi perto
        for (let x = 0; x < 3; x++) {
            icons[x].setAttribute('src', 'items/' + results[x] + '.png');
            icons[(icons.length - 3) + x].setAttribute('src', 'items/' + results[x] + '.png');
        }
    }
    if (results[0] == results[1] == results[2]){
        window.alert("you won!!");
    }
}

function getRandomIcon() {
    return ICONS[Math.floor(Math.random() * ICONS.length)];
}

/**
 * @returns {number} 0.00 to 0.09 inclusive
 */
function randomDuration() {
    return Math.floor(Math.random() * 10) / 100;
}