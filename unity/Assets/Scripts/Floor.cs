using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum FloorState
{
    None,
    CalledFromInside,
    CalledFromOutside,
    CalledFromBoth
}


[System.Serializable]
public class Floor : MonoBehaviour
{
    public Transform floorTransform; // Позиция этажа
    public int floorNumber; // Номер этажа
    public Renderer floorRenderer;
    
    private FloorState _state = FloorState.None;
    
    public void Initialize(int number, Transform transform, Renderer renderer)
    {
        floorNumber = number;
        floorTransform = transform;
        floorRenderer = renderer;
        _state = FloorState.None;
    }
    
    void Awake()
    {
        floorTransform = this.transform; // Автоматически присваиваем transform объекта этажа

        if (!floorRenderer) // Если floorRenderer не установлен
        {
            floorRenderer = GetComponent<MeshRenderer>(); // Пытаемся автоматически получить компонент MeshRenderer
        }

        if (!floorRenderer) // Если после попытки он все равно не установлен
        {
            Debug.LogError("No MeshRenderer found on the floor object!", this);
        }
    }

    public FloorState State 
    {
        get { return _state; }
        set 
        {
            _state = value;
            UpdateFloorColor();
        }
    }

    public void UpdateFloorColor()
    {
        Color newColor = Color.white; // Белый цвет по умолчанию

        switch (_state)
        {
            case FloorState.None:
                newColor = Color.white;
                break;
            case FloorState.CalledFromInside:
                newColor = Color.blue;
                break;
            case FloorState.CalledFromOutside:
                newColor = Color.red;
                break;
            case FloorState.CalledFromBoth:
                newColor = Color.magenta; // комбинация красного и синего
                break;
        }

        if (floorRenderer != null)
        {
            floorRenderer.material.color = newColor;
        }

    }
}
