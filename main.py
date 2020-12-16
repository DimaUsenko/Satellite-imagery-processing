import cv2
#import overpass
import numpy as np

E = -600, 550 #Погрешность, вычисленная опытным путем

k1=1483, 24 #координаты крайних точек в пикселях
k2=7671, 1100
k3=6300,7112
k4=39,6023

screen_res = 1280, 720


def get_mean(word):
    """Парсер для нахождения значения углов"""

    inp = open('LE07_L1TP_044034_20021222_20160927_01_T1_MTL.txt').readlines()
    for i in iter(inp):
        if word in i:
            original = i[4:]
            return float(original.replace(word + " = ", ""))

def get_point(p1,p2,coeff):
    """Деление отрезка в данном отношении, возвращает координаты точки М"""

    l = coeff / (1 - coeff) #получаем лямбду из формулы деления отрезка в данном отношении
    if coeff<=0.5:
        xm = int((p1[0] + l * p2[0]) / (1 + l))
        ym = int((p1[1] + l * p2[1]) / (1 + l))
        M = xm,ym
        return M
    else:
        l = 1/l
        xm = int((p2[0] + l * p1[0]) / (1 + l))
        ym = int((p2[1] + l * p1[1]) / (1 + l))
        M = xm, ym
        return M

def show_result(result):
    """Выводит изображение в удобном разрешении"""
    scale_width = screen_res[0] / result.shape[1]
    scale_height = screen_res[1] / result.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(result.shape[1] * scale)
    window_height = int(result.shape[0] * scale)

    cv2.namedWindow('Ndvi', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Ndvi', window_width, window_height)

    cv2.imshow('Ndvi', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_city_coordinates(city):
    '''Получаем координаты города'''
    api = overpass.API()
    response = api.get('node["name"="{}"]'.format(city))
    return response['features'][0]['geometry']['coordinates']

def make(POINT):
    CORNER_UL = get_mean('CORNER_UL_LAT_PRODUCT'), get_mean('CORNER_UL_LON_PRODUCT')
    CORNER_UR = get_mean('CORNER_UR_LAT_PRODUCT'), get_mean('CORNER_UR_LON_PRODUCT')
    CORNER_LL = get_mean('CORNER_LL_LAT_PRODUCT'), get_mean('CORNER_LL_LON_PRODUCT')
    CORNER_LR = get_mean('CORNER_LR_LAT_PRODUCT'), get_mean('CORNER_LR_LON_PRODUCT')

    delta_lat = (CORNER_UL[0] + CORNER_UR[0]) / 2 - (
            CORNER_LL[0] + CORNER_LR[0]) / 2
    delta_lon = abs(
        (CORNER_UL[1] + CORNER_LL[1]) / 2 - (CORNER_UR[1] + CORNER_LR[1]) / 2)

    kx = (abs((CORNER_UL[1] + CORNER_LL[1]) / 2) - abs(POINT[1])) / delta_lon
    ky = (POINT[0] - (CORNER_LL[0] + CORNER_LR[0]) / 2) / delta_lat

    m1 = get_point(k1, k2, kx)
    m2 = get_point(k4, k1, ky)

    img = cv2.imread("LE07_L1TP_044034_20021222_20160927_01_T1_B1.TIF")
    # img = cv2.line(img, (k1[0], k1[ 1]), (int(m1[0]), int(m1[1])), (0, 255, 0), 10) #векторы
    # img = cv2.line(img, (k4[0], k4[1]), (int(m2[0]), int(m2[1])), (0, 255, 0), 10)

    answer = (m1[0] + E[0]),(m2[1] + E[1])

    #img = cv2.circle(img, (answer[0], answer[1]), 500, (0, 0, 255), thickness=10)
    cv2.putText(
        img,
        POINT[2],  # text
        (m1[0] + 500, m2[1] + 500),
        cv2.FONT_HERSHEY_SIMPLEX,
        8,
        (255, 255, 255),
        10)
    cv2.putText(
        img,
        'City lat lon: {}, {}'.format(POINT[0], POINT[1]),
        (150, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        4,
        (255, 255, 255),
        10)
    cv2.putText(
        img,
        'Delta: {}, {}'.format(delta_lat, delta_lon),
        (150, 350),
        cv2.FONT_HERSHEY_SIMPLEX,
        4,
        (255, 255, 255),
        10)
    cv2.putText(
        img,
        'Coefficient: {}, {}'.format(kx, ky),
        (150, 550),
        cv2.FONT_HERSHEY_SIMPLEX,
        4,
        (255, 255, 255),
        10)
    cv2.putText(
        img,
        'Point coordinates: {}, {}'.format(m1, m2),  (150, 750),cv2.FONT_HERSHEY_SIMPLEX,4,(255, 255, 255),10)

    cut_list = [(answer[0] - 1000, answer[1] - 1000), (answer[0] + 1000, answer[1] - 1000),
                (answer[0] + 1000, answer[1] + 1000), (answer[0] - 1000, answer[1] + 1000)]

    img = cv2.line(img, cut_list[0], cut_list[1], (0,0,255), 15)
    img = cv2.line(img, cut_list[1], cut_list[2], (0,0,255), 15)
    img = cv2.line(img, cut_list[2], cut_list[3], (0,0,255), 15)
    img = cv2.line(img, cut_list[3], cut_list[0], (0,0,255), 15)

    show_result(img)

    return answer


def cut_image(image,y1,y2,x1,x2):
    img = cv2.imread(image)
    crop_img = img[y1:y2, x1:x2]
    return crop_img

def add_colormap(gr, colormap):
     return cv2.LUT((gr * 256).astype("uint8"), colormap.astype("uint8"));

if __name__ == '__main__':

    '''Поинты основных городов:
        POINT = 36.958671131530316, -122.03887939453126, 'Santa Cruz'
        #POINT = 37.326488613342086, -121.89880371093751 ,'San Joze'
        #POINT = 37.97018468810549, -122.04986572265626 ,'Concord'
        #POINT = 37.779026, -122.419906 ,'San Francisco'
        '''
    POINT = 37.779026, -122.419906 ,'San Francisco'

    # city = input('Введите название города: ') #Работает не для всех городов
    # POINT = get_city_coordinates(city)[1], get_city_coordinates(city)[0], city

    a=make(POINT)

    y1,y2,x1,x2 = a[1]-1000,a[1]+1000,a[0]-1000,a[0]+1000 #координаты обрезанного города

    cut_image("LE07_L1TP_044034_20021222_20160927_01_T1_B1.TIF",y1,y2,x1,x2)

    red_img = cut_image('LE07_L1TP_044034_20021222_20160927_01_T1_B3.tif',y1,y2,x1,x2)
    nir_img = cut_image('LE07_L1TP_044034_20021222_20160927_01_T1_B4.tif',y1,y2,x1,x2)

    nir_mat_float = red_img.astype(float)
    red_mat_float = nir_img.astype(float)

    gr = (np.divide(np.subtract(nir_mat_float, red_mat_float), np.add(nir_mat_float, red_mat_float)) + 1.) / 2.

    colormap = cv2.imread('colormap2.png')
    final = add_colormap(gr, colormap)

    show_result(final)







