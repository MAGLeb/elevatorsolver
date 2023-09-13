using UnityEngine;
using UnityEngine.UI;

public class FloorButtonController : MonoBehaviour
{
    public Floor floor; // Ссылка на объект этажа, который контролирует кнопка
    public FloorState targetState; // Состояние, на которое нужно изменить этаж

    private Button _button;

    private void Awake()
    {
        _button = GetComponent<Button>();
        _button.onClick.AddListener(HandleButtonClick);
    }

    private void HandleButtonClick()
    {
        if (floor != null)
        {
            floor.State = targetState;
        }
    }
}