import plotly.graph_objects as go
import utilities.coord_csv_module as ccsv

coordinates = ccsv.csv_to_list('flight_logs/2024-06-07_01-06-23.csv')

print(coordinates)
# her uclunun sonuna 1 ekleme
coordinates = [coord + (1,) for coord in coordinates]

# ardisik ayni noktalari silip, current noktanin 4. elemanini 1 arttirma,
# boylece her noktada kac kere kalindigini buluyoruz

i = 0
while i < len(coordinates) - 1:
    while coordinates[i][:3] == coordinates[i + 1][:3]:
        coordinates[i] = coordinates[i][:3] + (coordinates[i][3] + 1,)
        coordinates.pop(i + 1)
        
        if i == len(coordinates) - 1:
            break
    i += 1

# map fonksiyonundaki interval 0.25 oldugu icin count degerlerini 4e bolup
# her noktada kac saniye kalindigini buluyoruz
    
coordinates = [coord[:3] + (coord[3] << 2,) for coord in coordinates]

x, y, z, time = zip(*coordinates)

fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(
        size= 8,
        color = time,
        colorscale='Bluered',
        opacity= 0.7,
        
    ), hovertemplate='(%{x}, %{y}, %{z})<br>Time: %{marker.color} seconds<br>')],)


fig.update_layout(scene=dict(xaxis_title='X Axis', yaxis_title='Y Axis', zaxis_title='Z Axis'))

fig.show()