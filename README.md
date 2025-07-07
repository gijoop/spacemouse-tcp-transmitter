## Podstawowe informacje

### Instalacja
- wymagane jest zainstalowanie sterowników do spacemouse: w przypadku windowsa oryginalnych ze strony 3D connexion w przypadku linuxa najlepiej sprawdzają się [te](https://github.com/FreeSpacenav/spacenavd). Na linuxie należy włączyć sterowniki z użyciem systemctl `sudo systemctl start spacenavd`

- wymagana może być instalacja biblioteki libhidapi-dev, na ubuntu instaluje się ją: `sudo apt install libhidapi-dev`

### Uruchomienie

- skrypt uruchamia się z użyciem start.sh, który konfiguruje środowisko *skrypt istnieje na razie tylko na linuxa* na windowsie należy zbudować środowisko wirtualne pythona z użyciem requirements.txt

### Działanie
- w kodzie należy ustawić adresy ip serwera
- po wysłaniu 10 pustych wartości spacemouse przestaje przesyłać informacje przez tcp, czeka na zmianę wartości

## Kod używany był tylko z wersją Enterprise
