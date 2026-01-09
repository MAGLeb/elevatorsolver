using System.Collections;
using UnityEngine;

public class ElevatorController : MonoBehaviour
{
    public Transform leftDoor;
    public Transform rightDoor;

    private Vector3 leftDoorClosedPosition;
    private Vector3 rightDoorClosedPosition;
    private bool isDoorOpen = false;
    private bool isMoving = false;
    private bool isDoorsMoving = false;

    public float speed = 5.0f;
    public float doorSpeed = 5.0f;
    public float doorWidth = 0.35f;

    private Vector3 targetPosition;
    private Coroutine moveCoroutine;
    private Coroutine doorCoroutine;

    public Floor[] floors;
    public TextMesh weightDisplay;

    void Start()
    {
        leftDoorClosedPosition = leftDoor.localPosition;
        rightDoorClosedPosition = rightDoor.localPosition;
    }

    public void PerformAction(int action)
    {
        switch (action)
        {
            case 0: // UP
                MoveUp();
                break;
            case 1: // DOWN
                MoveDown();
                break;
            case 2: // WAIT - ничего не делаем
                break;
            case 3: // STOP - открыть, подождать, закрыть
                StopAndService();
                break;
        }
    }

    public void StopAndService()
    {
        if (!isDoorsMoving && !isMoving)
        {
            if (doorCoroutine != null)
                StopCoroutine(doorCoroutine);
            doorCoroutine = StartCoroutine(OpenThenCloseDoors());
        }
    }

    private IEnumerator OpenThenCloseDoors()
    {
        // Открываем двери
        isDoorsMoving = true;
        Vector3 leftDoorOpenPosition = leftDoorClosedPosition + new Vector3(0, 0, doorWidth);
        Vector3 rightDoorOpenPosition = rightDoorClosedPosition + new Vector3(0, 0, -doorWidth);

        while (Vector3.Distance(leftDoor.localPosition, leftDoorOpenPosition) > 0.01f)
        {
            leftDoor.localPosition = Vector3.MoveTowards(leftDoor.localPosition, leftDoorOpenPosition, doorSpeed * Time.deltaTime);
            rightDoor.localPosition = Vector3.MoveTowards(rightDoor.localPosition, rightDoorOpenPosition, doorSpeed * Time.deltaTime);
            yield return null;
        }
        leftDoor.localPosition = leftDoorOpenPosition;
        rightDoor.localPosition = rightDoorOpenPosition;
        isDoorOpen = true;

        // Ждём немного (пассажиры входят/выходят)
        yield return new WaitForSeconds(0.3f);

        // Закрываем двери
        while (Vector3.Distance(leftDoor.localPosition, leftDoorClosedPosition) > 0.01f)
        {
            leftDoor.localPosition = Vector3.MoveTowards(leftDoor.localPosition, leftDoorClosedPosition, doorSpeed * Time.deltaTime);
            rightDoor.localPosition = Vector3.MoveTowards(rightDoor.localPosition, rightDoorClosedPosition, doorSpeed * Time.deltaTime);
            yield return null;
        }
        leftDoor.localPosition = leftDoorClosedPosition;
        rightDoor.localPosition = rightDoorClosedPosition;
        isDoorOpen = false;
        isDoorsMoving = false;
    }

    public void CallElevator(int floorNumber)
    {
        if (floorNumber >= 0 && floorNumber < floors.Length && !isMoving)
        {
            targetPosition = new Vector3(transform.position.x, floors[floorNumber].transform.position.y, transform.position.z);
            if (moveCoroutine != null)
                StopCoroutine(moveCoroutine);
            moveCoroutine = StartCoroutine(MoveToTargetFloor());
        }
    }

    public void MoveUp()
    {
        if (!isMoving && transform.position.y < floors[floors.Length - 1].transform.position.y)
        {
            CallElevator(GetCurrentFloorNumber() + 1);
        }
    }

    public void MoveDown()
    {
        if (!isMoving && transform.position.y > floors[0].transform.position.y)
        {
            CallElevator(GetCurrentFloorNumber() - 1);
        }
    }

    public void OpenDoor()
    {
        if (!isDoorsMoving && !isDoorOpen && !isMoving)
        {
            if (doorCoroutine != null)
                StopCoroutine(doorCoroutine);
            doorCoroutine = StartCoroutine(OpenDoors());
        }
    }

    public void CloseDoor()
    {
        if (!isDoorsMoving && isDoorOpen && !isMoving)
        {
            if (doorCoroutine != null)
                StopCoroutine(doorCoroutine);
            doorCoroutine = StartCoroutine(CloseDoors());
        }
    }

    private int GetCurrentFloorNumber()
    {
        float closestDistance = float.MaxValue;
        int closestFloorNumber = 0;

        for (int i = 0; i < floors.Length; i++)
        {
            float distance = Mathf.Abs(transform.position.y - floors[i].transform.position.y);
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestFloorNumber = i;
            }
        }

        return closestFloorNumber;
    }

    private IEnumerator MoveToTargetFloor()
    {
        isMoving = true;

        while (Vector3.Distance(transform.position, targetPosition) > 0.01f)
        {
            transform.position = Vector3.MoveTowards(transform.position, targetPosition, speed * Time.deltaTime);
            yield return null;
        }

        transform.position = targetPosition;
        isMoving = false;
    }

    private IEnumerator OpenDoors()
    {
        isDoorsMoving = true;

        Vector3 leftDoorOpenPosition = leftDoorClosedPosition + new Vector3(0, 0, doorWidth);
        Vector3 rightDoorOpenPosition = rightDoorClosedPosition + new Vector3(0, 0, -doorWidth);

        while (Vector3.Distance(leftDoor.localPosition, leftDoorOpenPosition) > 0.01f)
        {
            leftDoor.localPosition = Vector3.MoveTowards(leftDoor.localPosition, leftDoorOpenPosition, doorSpeed * Time.deltaTime);
            rightDoor.localPosition = Vector3.MoveTowards(rightDoor.localPosition, rightDoorOpenPosition, doorSpeed * Time.deltaTime);
            yield return null;
        }

        leftDoor.localPosition = leftDoorOpenPosition;
        rightDoor.localPosition = rightDoorOpenPosition;
        isDoorOpen = true;
        isDoorsMoving = false;
    }

    private IEnumerator CloseDoors()
    {
        isDoorsMoving = true;

        while (Vector3.Distance(leftDoor.localPosition, leftDoorClosedPosition) > 0.01f)
        {
            leftDoor.localPosition = Vector3.MoveTowards(leftDoor.localPosition, leftDoorClosedPosition, doorSpeed * Time.deltaTime);
            rightDoor.localPosition = Vector3.MoveTowards(rightDoor.localPosition, rightDoorClosedPosition, doorSpeed * Time.deltaTime);
            yield return null;
        }

        leftDoor.localPosition = leftDoorClosedPosition;
        rightDoor.localPosition = rightDoorClosedPosition;
        isDoorOpen = false;
        isDoorsMoving = false;
    }

    public void UpdatePassengersWeight(int currentWeight, int maxWeight)
    {
        if (weightDisplay != null)
        {
            weightDisplay.text = currentWeight + "/" + maxWeight;
        }
    }
}
