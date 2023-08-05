easy-mask
============

Um simples pacote para uso de máscaras no django


Instalação
----------

    pip install easy-mask
    
    
Configuração
------------

Adicione o pacote ao INSTALLED_APPS

para usar o mesmo basta adicionar {% load easy_mask %} no inicio de template/html .

exemplo de uso
--------------

    {% for data in personal %}
      <tr>
        <td>{{ data.cpf | cpf }}</td>
        <td>{{ data.phone | phone }}</td>
        <td>{{ data.cnpj | cnpj }}</td>
        <td>{{ data.cep | cep }}</td>
      </tr>
    {% endfor %}

observação
----------

As máscaras existentes são

- phone
- cnpj
- cpf
- cep

Repositório do projeto no Github: https://github.com/dhelbegor/easy-mask .